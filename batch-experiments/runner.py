#!/usr/bin/env python3
"""Batch experiment runner for code-golf.

Simple orchestrator: for each (method, task, trial) combo,
runs `claude --dangerously-skip-permissions "read agent.md and start working"`
in the experiment directory. Tracks progress in a state file, supports resume.
"""

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
EXPERIMENTS_DIR = os.path.join(SCRIPT_DIR, "experiments")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results")

# ── Experiment matrix ──────────────────────────────────────────
TASKS = list(range(1, 11))  # task001 – task010
METHODS = ["comap", "comap_claude", "baseline", "auto_pal", "default"]
DEFAULT_TRIALS = 3
DEFAULT_PARALLEL = 8

CLAUDE_BINARY = "claude"
CLAUDE_ARGS = ["--dangerously-skip-permissions"]
CLAUDE_PROMPT = "read agent.md and start working"

# ── Helpers ────────────────────────────────────────────────────


def job_id(method: str, task: int, trial: int) -> str:
    return f"{method}_task{task:03d}_trial{trial}"


def run_dir() -> str:
    """Create a timestamped run directory."""
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    path = os.path.join(RESULTS_DIR, ts)
    os.makedirs(path, exist_ok=True)
    return path


def load_state(state_path: str) -> dict:
    """Load existing state, or return fresh state dict."""
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            return json.load(f)
    return {
        "run_id": os.path.basename(os.path.dirname(state_path)),
        "started_at": datetime.now().isoformat(),
        "jobs": {},
    }


def save_state(state_path: str, state: dict):
    """Thread-safe atomic save to disk using per-thread temp file."""
    tmp = f"{state_path}.tmp.{threading.get_ident()}"
    state["updated_at"] = datetime.now().isoformat()
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, default=str)
    os.replace(tmp, state_path)  # atomic on same filesystem


def scan_best_bytes(workdir: str) -> Optional[int]:
    """Scan workdir for the smallest v*.py file (in bytes)."""
    if not os.path.isdir(workdir):
        return None
    best = None
    for fname in os.listdir(workdir):
        if not fname.endswith(".py"):
            continue
        fpath = os.path.join(workdir, fname)
        try:
            size = os.path.getsize(fpath)
            if best is None or size < best:
                best = size
        except OSError:
            pass
    return best


# ── Job execution ──────────────────────────────────────────────


def run_job(method: str, task: int, trial: int, run_dir_path: str, state: dict) -> dict:
    """Run a single Claude Code experiment job. Returns job result dict."""
    job_key = job_id(method, task, trial)
    task_str = f"task{task:03d}"
    cwd = os.path.join(EXPERIMENTS_DIR, method, task_str)

    if not os.path.isdir(cwd):
        return {
            "state": "failed",
            "error": f"Directory not found: {cwd}",
            "method": method,
            "task": task,
            "trial": trial,
        }

    # ── Log stderr per job for debugging ──
    logs_dir = os.path.join(run_dir_path, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file = os.path.join(logs_dir, f"{job_key}.log")

    # Build command
    cmd = [CLAUDE_BINARY] + CLAUDE_ARGS + [CLAUDE_PROMPT]

    print(f"[{job_key}] Starting in {cwd}", flush=True)
    started_at = time.time()

    try:
        with open(log_file, "w") as log_f:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=log_f,
                stderr=subprocess.STDOUT,
            )
            try:
                proc.wait(timeout=7200)  # 2 hour timeout
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                elapsed = time.time() - started_at
                return {
                    "state": "timeout",
                    "error": "Job exceeded 2 hour timeout",
                    "method": method,
                    "task": task,
                    "trial": trial,
                    "duration_seconds": round(elapsed, 1),
                    "log_file": log_file,
                }
        elapsed = time.time() - started_at
    except Exception as e:
        return {
            "state": "failed",
            "error": str(e),
            "method": method,
            "task": task,
            "trial": trial,
            "duration_seconds": time.time() - started_at,
        }

    # Scan results
    workdir = os.path.join(cwd, "workdir")
    best_bytes = scan_best_bytes(workdir)

    result = {
        "state": "completed" if proc.returncode == 0 else "failed",
        "method": method,
        "task": task,
        "trial": trial,
        "exit_code": proc.returncode,
        "duration_seconds": round(elapsed, 1),
        "best_bytes": best_bytes,
        "cwd": cwd,
        "log_file": log_file,
    }

    status = f"{best_bytes}B" if best_bytes else "N/A"
    print(f"[{job_key}] Done in {elapsed:.0f}s — best: {status}", flush=True)
    return result


# ── Main orchestrator ──────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Batch code-golf experiment runner"
    )
    parser.add_argument(
        "--tasks", type=str, default="1-10",
        help="Task range, e.g. '1-5' or '1,3,5' (default: 1-10)"
    )
    parser.add_argument(
        "--methods", type=str, default="comap,comap_claude,baseline,auto_pal,default",
        help="Comma-separated methods"
    )
    parser.add_argument(
        "--trials", type=int, default=DEFAULT_TRIALS,
        help=f"Trials per combo (default: {DEFAULT_TRIALS})"
    )
    parser.add_argument(
        "--parallel", type=int, default=DEFAULT_PARALLEL,
        help=f"Max concurrent Claude processes (default: {DEFAULT_PARALLEL})"
    )
    parser.add_argument(
        "--resume", type=str, default=None,
        help="Resume from a previous run directory (e.g., results/20260714-120000)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print jobs without executing"
    )
    args = parser.parse_args()

    # Parse task list
    tasks = []
    for part in args.tasks.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            tasks.extend(range(int(lo), int(hi) + 1))
        else:
            tasks.append(int(part))

    methods = [m.strip() for m in args.methods.split(",")]

    # ── Build job matrix ───────────────────────────────────────
    all_jobs = [
        (m, t, trial)
        for m in methods
        for t in tasks
        for trial in range(1, args.trials + 1)
    ]

    total = len(all_jobs)
    print(f"Experiment matrix: {len(methods)} methods × {len(tasks)} tasks "
          f"× {args.trials} trials = {total} jobs")
    print(f"Parallel workers: {args.parallel}")
    print()

    # ── Set up run directory and state ─────────────────────────
    if args.resume:
        run_dir_path = os.path.abspath(args.resume)
        if not os.path.isdir(run_dir_path):
            print(f"Run directory not found: {run_dir_path}")
            sys.exit(1)
        print(f"Resuming from: {run_dir_path}")
    else:
        run_dir_path = run_dir()
        print(f"Run directory: {run_dir_path}")

    state_path = os.path.join(run_dir_path, "state.json")
    state = load_state(state_path)

    # Filter to pending jobs
    pending = []
    skipped = 0
    for m, t, trial in all_jobs:
        jk = job_id(m, t, trial)
        if jk in state["jobs"] and state["jobs"][jk].get("state") == "completed":
            skipped += 1
            continue
        pending.append((m, t, trial))

    if skipped:
        print(f"Skipping {skipped} already-completed jobs")
    print(f"Jobs to run: {len(pending)}")
    print()

    if args.dry_run:
        for m, t, trial in pending:
            task_str = f"task{t:03d}"
            cwd = os.path.join(EXPERIMENTS_DIR, m, task_str)
            print(f"  [{job_id(m, t, trial)}] cd {cwd} && "
                  f"{CLAUDE_BINARY} {' '.join(CLAUDE_ARGS)} \"{CLAUDE_PROMPT}\"")
        return

    if not pending:
        print("All jobs already completed. Nothing to do.")
        return

    # ── Execute ─────────────────────────────────────────────────
    completed = 0
    failed = 0
    lock = threading.Lock()

    def run_and_track(m, t, trial):
        """Wrapper: run a job and update state."""
        jk = job_id(m, t, trial)
        with lock:
            state["jobs"][jk] = {"state": "running", "method": m, "task": t, "trial": trial}
            save_state(state_path, state)
        try:
            result = run_job(m, t, trial, run_dir_path, state)
        except Exception as e:
            result = {
                "state": "failed",
                "error": str(e),
                "method": m,
                "task": t,
                "trial": trial,
            }
        with lock:
            state["jobs"][jk] = result
            save_state(state_path, state)
        return result

    with ThreadPoolExecutor(max_workers=args.parallel) as pool:
        futures = {}
        for m, t, trial in pending:
            jk = job_id(m, t, trial)
            state["jobs"][jk] = {"state": "queued", "method": m, "task": t, "trial": trial}
            fut = pool.submit(run_and_track, m, t, trial)
            futures[fut] = (m, t, trial)
        save_state(state_path, state)

        for fut in as_completed(futures):
            m, t, trial = futures[fut]
            jk = job_id(m, t, trial)
            try:
                result = fut.result()
            except Exception as e:
                result = {
                    "state": "failed",
                    "error": str(e),
                    "method": m,
                    "task": t,
                    "trial": trial,
                }

            with lock:
                state["jobs"][jk] = result
                save_state(state_path, state)

            if result.get("state") == "completed":
                completed += 1
            else:
                failed += 1

            print(f"Progress: {completed} done, {failed} failed, "
                  f"{len(pending) - completed - failed} remaining", flush=True)

    # ── Final summary ──────────────────────────────────────────
    print()
    print(f"Run complete: {completed} succeeded, {failed} failed")
    print(f"Results: {run_dir_path}")

    # Quick summary table
    print()
    print("Summary by method:")
    for m in methods:
        mb = []
        for jk, jr in state["jobs"].items():
            if jr.get("method") == m and jr.get("state") == "completed":
                mb.append(jr.get("best_bytes"))
        if mb:
            valid = [b for b in mb if b is not None]
            if valid:
                print(f"  {m}: {len(valid)}/{len(mb)} runs, "
                      f"best={min(valid)}B, mean={sum(valid)/len(valid):.0f}B")
            else:
                print(f"  {m}: {len(mb)} runs, no results yet")


if __name__ == "__main__":
    main()
