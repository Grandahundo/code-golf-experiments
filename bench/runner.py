#!/usr/bin/env python3
"""Runner — schedules (task, model, seed) jobs with per-model concurrency.

Usage:
    python runner.py --config config.yaml
    python runner.py --config config.yaml --models deepseek-v4-pro --tasks tasks.txt --seeds 3
    python runner.py --config config.yaml --dry-run
"""

import argparse
import asyncio
import json
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

from task_loader import load_task, TaskBundle
from llm import LLMClient
from loop import run_job


# ── Config loading ───────────────────────────────────────────────────

def load_config(config_path: str) -> dict:
    """Load YAML config, resolve relative paths to absolute."""
    config_dir = os.path.dirname(os.path.abspath(config_path))
    with open(config_path) as f:
        cfg = yaml.safe_load(f)

    # Resolve paths relative to config file location
    for key in ("tasks_dir", "gen_dir"):
        if key in cfg:
            path = cfg[key]
            if not os.path.isabs(path):
                cfg[key] = os.path.normpath(os.path.join(config_dir, path))

    return cfg


# ── Task list parsing ────────────────────────────────────────────────

def load_task_list(tasks_arg: "str | None", tasks_dir: str) -> "list[str]":
    """Get list of task IDs to run.

    Args:
        tasks_arg: comma-separated ranges ("1-10,15,20-25"), a file path, or None.
        tasks_dir: directory containing task*.json files.

    Returns:
        sorted list of task IDs like ["task001", "task002", ...]
    """
    if tasks_arg is None:
        # All tasks in directory
        ids = []
        for fname in sorted(os.listdir(tasks_dir)):
            if fname.startswith("task") and fname.endswith(".json"):
                ids.append(fname.replace(".json", ""))
        return ids

    # Check if it's a file
    if os.path.isfile(tasks_arg):
        with open(tasks_arg) as f:
            ids = [line.strip() for line in f if line.strip()]
        return ids

    # Parse as comma-separated ranges
    ids = []
    for part in tasks_arg.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            for i in range(int(lo), int(hi) + 1):
                ids.append(f"task{i:03d}")
        else:
            ids.append(f"task{int(part):03d}")
    return ids


# ── Main ─────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Code Golf Benchmark Runner")
    parser.add_argument("--config", required=True, help="Path to config.yaml")
    parser.add_argument("--models", default=None,
                        help="Comma-separated model keys (default: all in config)")
    parser.add_argument("--tasks", default=None,
                        help="Task IDs: range (1-10), file (tasks.txt), or comma list")
    parser.add_argument("--seeds", type=int, default=3,
                        help="Number of seeds per (task, model) combo")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print job matrix and estimated cost, then exit")
    parser.add_argument("--output-dir", default=None,
                        help="Override output directory (default: bench/runs)")
    args = parser.parse_args()

    # ── Load config ──────────────────────────────────────────────
    config_path = os.path.abspath(args.config)
    cfg = load_config(config_path)

    tasks_dir = cfg["tasks_dir"]
    gen_dir = cfg.get("gen_dir", "")
    runs_dir = args.output_dir or os.path.join(os.path.dirname(config_path), "runs")

    # ── Determine models ─────────────────────────────────────────
    all_models = list(cfg.get("models", {}).keys())
    if args.models:
        selected_models = [m.strip() for m in args.models.split(",")]
        for m in selected_models:
            if m not in all_models:
                print(f"Unknown model: {m}. Known: {all_models}")
                sys.exit(1)
    else:
        selected_models = all_models

    if not selected_models:
        print("No models configured.")
        sys.exit(1)

    # ── Determine tasks ──────────────────────────────────────────
    task_ids = load_task_list(args.tasks, tasks_dir)
    if not task_ids:
        print(f"No tasks found in {tasks_dir}")
        sys.exit(1)

    seeds = list(range(1, args.seeds + 1))

    # ── Build job matrix ─────────────────────────────────────────
    jobs = [
        (tid, mid, seed)
        for tid in task_ids
        for mid in selected_models
        for seed in seeds
    ]

    print(f"Config:    {config_path}")
    print(f"Output:    {runs_dir}")
    print(f"Models:    {', '.join(selected_models)}")
    print(f"Tasks:     {len(task_ids)} ({task_ids[0]} .. {task_ids[-1]})")
    print(f"Seeds:     {args.seeds}")
    print(f"Jobs:      {len(jobs)}")
    print()

    # ── Dry run ──────────────────────────────────────────────────
    if args.dry_run:
        _estimate_cost(jobs, cfg, task_ids, tasks_dir, gen_dir)
        return

    # ── Load task bundles (cached in memory) ─────────────────────
    print("Loading task bundles...")
    bundles: dict[str, TaskBundle] = {}
    for tid in task_ids:
        task_path = os.path.join(tasks_dir, f"{tid}.json")
        if not os.path.exists(task_path):
            print(f"  WARNING: {task_path} not found, skipping {tid}")
            continue
        bundles[tid] = load_task(
            task_path, gen_dir,
            gen_max_chars=cfg.get("gen_source_max_chars", 8000),
        )
    print(f"  Loaded {len(bundles)} tasks.\n")

    # ── Initialize LLM client ────────────────────────────────────
    llm = LLMClient(cfg)

    # ── Per-model semaphores ─────────────────────────────────────
    semaphores = {
        mid: asyncio.Semaphore(cfg["models"][mid].get("max_concurrency", 8))
        for mid in selected_models
    }

    # ── Progress tracking ────────────────────────────────────────
    total_jobs = len(jobs)
    completed = 0
    failed = 0
    skipped = 0
    lock = asyncio.Lock()
    last_progress = time.time()
    start_time = time.time()

    # ── Signal handling ──────────────────────────────────────────
    shutdown = asyncio.Event()

    def _handle_sig(signum, frame):
        print("\nInterrupted — waiting for running jobs to finish...")
        shutdown.set()

    signal.signal(signal.SIGINT, _handle_sig)
    signal.signal(signal.SIGTERM, _handle_sig)

    # ── Job runner ───────────────────────────────────────────────
    async def run_one(tid: str, mid: str, seed: int):
        nonlocal completed, failed, skipped, last_progress

        if shutdown.is_set():
            return

        output_dir = os.path.join(runs_dir, mid, tid, f"seed{seed}")

        # Check if already finished
        meta_path = os.path.join(output_dir, "meta.json")
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                meta = json.load(f)
            if meta.get("finished"):
                async with lock:
                    skipped += 1
                return

        async with semaphores[mid]:
            if shutdown.is_set():
                return

            try:
                bundle = bundles[tid]
                state = await run_job(bundle, mid, llm, seed, cfg, output_dir)

                async with lock:
                    completed += 1
                    _maybe_progress(lock, completed, failed, skipped, total_jobs,
                                    start_time, last_progress)

            except Exception as e:
                async with lock:
                    failed += 1
                print(f"\n  [{mid}/{tid}/seed{seed}] FAILED: {e}", flush=True)
                # Write a failure meta
                os.makedirs(output_dir, exist_ok=True)
                with open(os.path.join(output_dir, "meta.json"), "w") as f:
                    json.dump({
                        "task_id": tid, "model": mid, "seed": seed,
                        "finished": False, "error": str(e),
                    }, f, indent=2)

    # ── Launch all jobs ──────────────────────────────────────────
    tasks = [run_one(tid, mid, seed) for tid, mid, seed in jobs]
    await asyncio.gather(*tasks, return_exceptions=True)

    # ── Final summary ────────────────────────────────────────────
    elapsed = time.time() - start_time
    print(f"\n{'=' * 60}")
    print(f"Run complete: {completed} done, {failed} failed, {skipped} skipped")
    print(f"Total time: {elapsed:.0f}s ({elapsed/60:.1f}m)")
    print(f"Output: {runs_dir}")


def _maybe_progress(lock, completed, failed, skipped, total, start_time, last_progress):
    """Print progress at intervals."""
    now = time.time()
    if now - last_progress < 60:
        return
    elapsed = now - start_time
    done = completed + failed + skipped
    rate = done / elapsed * 60 if elapsed > 0 else 0
    print(f"\nProgress: {done}/{total} jobs ({completed} done, {failed} failed, "
          f"{skipped} skipped) — {rate:.1f}/min", flush=True)
    last_progress = now


def _estimate_cost(jobs, cfg, task_ids, tasks_dir, gen_dir):
    """Print cost estimate for a dry run."""
    # Estimate per-job tokens: ~12k input, ~2k output = 14k tokens
    # Over 30 rounds: ~420k tokens
    est_input_per_job = 360_000   # 12k * 30
    est_output_per_job = 60_000   # 2k * 30

    total_cost = 0.0
    print("Cost Estimate:")
    print(f"  Per-job estimate: ~{est_input_per_job/1000:.0f}K input + "
          f"~{est_output_per_job/1000:.0f}K output tokens")

    by_model = {}
    for tid, mid, seed in jobs:
        by_model.setdefault(mid, 0)
        by_model[mid] += 1

    for mid, count in by_model.items():
        mcfg = cfg.get("models", {}).get(mid, {})
        prices = mcfg.get("price_per_mtok", {})
        input_price = prices.get("input", 0)
        output_price = prices.get("output", 0)

        total_input = est_input_per_job * count / 1_000_000
        total_output = est_output_per_job * count / 1_000_000
        cost = total_input * input_price + total_output * output_price
        total_cost += cost

        print(f"\n  {mid}: {count} jobs")
        print(f"    Est tokens: {total_input:.0f}M in + {total_output:.0f}M out")
        print(f"    Est cost: ${cost:.2f}")

    print(f"\n  TOTAL estimated cost: ${total_cost:.2f}")
    print(f"\n  Actual tasks: {len(task_ids)}, Models: {len(set(m for _, m, _ in jobs))}, "
          f"Seeds: {len(set(s for _, _, s in jobs))}")


if __name__ == "__main__":
    asyncio.run(main())
