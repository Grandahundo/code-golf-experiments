#!/usr/bin/env python3
"""Batch experiment runner — simple: run claude, wait for it to finish, record result.

Each trial has its OWN isolated workdir. No timeout, no auto-kill.
Claude runs until it decides to stop.
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
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RUNS_DIR = os.path.join(SCRIPT_DIR, "runs")

# ── Experiment matrix ──────────────────────────────────────────
TASKS = list(range(1, 11))
METHODS = ["comap", "comap_claude", "baseline", "auto_pal", "default"]
DEFAULT_TRIALS = 3
DEFAULT_PARALLEL = 8

CLAUDE_BINARY = "claude"
CLAUDE_ARGS = ["--dangerously-skip-permissions"]
CLAUDE_PROMPT = "read agent.md and start working"


def job_id(method: str, task: int, trial: int) -> str:
    return f"{method}_task{task:03d}_trial{trial}"


def load_state(state_path: str) -> dict:
    if os.path.exists(state_path):
        with open(state_path, "r") as f:
            return json.load(f)
    return {
        "started_at": datetime.now().isoformat(),
        "jobs": {},
    }


def save_state(state_path: str, state: dict):
    tmp = f"{state_path}.tmp.{threading.get_ident()}"
    state["updated_at"] = datetime.now().isoformat()
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, default=str)
    os.replace(tmp, state_path)


def scan_best_bytes(workdir: str) -> Optional[int]:
    if not os.path.isdir(workdir):
        return None
    best = None
    for fname in os.listdir(workdir):
        if not fname.endswith(".py"):
            continue
        try:
            size = os.path.getsize(os.path.join(workdir, fname))
            if best is None or size < best:
                best = size
        except OSError:
            pass
    return best


def run_job(method: str, task: int, trial: int, exp_dir: str) -> dict:
    """Run one Claude Code session in an isolated trial directory."""
    task_str = f"task{task:03d}"
    cwd = os.path.join(exp_dir, method, task_str, f"trial_{trial}")

    if not os.path.isdir(cwd):
        return {"state": "failed", "error": f"Directory not found: {cwd}"}

    cmd = [CLAUDE_BINARY] + CLAUDE_ARGS + [CLAUDE_PROMPT]
    jk = job_id(method, task, trial)

    print(f"[{jk}] Starting in {cwd}", flush=True)
    started_at = time.time()

    try:
        proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        proc.wait()
        elapsed = time.time() - started_at
    except Exception as e:
        return {"state": "failed", "error": str(e), "duration_seconds": time.time() - started_at}

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
    }

    status = f"{best_bytes}B" if best_bytes else "N/A"
    print(f"[{jk}] Done in {elapsed:.0f}s — best: {status}", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description="Batch code-golf experiment runner")
    parser.add_argument("--tasks", type=str, default="1-10")
    parser.add_argument("--methods", type=str, default="comap,comap_claude,baseline,auto_pal,default")
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--parallel", type=int, default=DEFAULT_PARALLEL)
    parser.add_argument("--resume", type=str, default=None,
                        help="Resume from a run directory (e.g., runs/20260715-120000)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Parse args
    tasks = []
    for part in args.tasks.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            tasks.extend(range(int(lo), int(hi) + 1))
        else:
            tasks.append(int(part))
    methods = [m.strip() for m in args.methods.split(",")]

    # ── Set up run directory ───────────────────────────────────
    if args.resume:
        run_dir = os.path.abspath(args.resume)
        if not os.path.isdir(run_dir):
            print(f"Run directory not found: {run_dir}")
            sys.exit(1)
        print(f"Resuming: {run_dir}")
    else:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = os.path.join(RUNS_DIR, ts)
        os.makedirs(run_dir, exist_ok=True)
        # Check if scaffolded — if not, scaffold
        exp_dir = os.path.join(run_dir, "experiments")
        if not os.path.isdir(exp_dir):
            print("Experiments not scaffolded. Run scaffold.py first:")
            print(f"  python3 batch-experiments/scaffold.py --tasks {args.tasks} --methods {args.methods} --trials {args.trials}")
            print("Then pass --resume to this runner to use the scaffolded directory.")
            sys.exit(1)
        print(f"Run directory: {run_dir}")

    exp_dir = os.path.join(run_dir, "experiments")
    state_path = os.path.join(run_dir, "state.json")
    state = load_state(state_path)

    # ── Build job matrix, filter completed ─────────────────────
    all_jobs = [(m, t, trial)
                for m in methods for t in tasks
                for trial in range(1, args.trials + 1)]
    pending = []
    skipped = 0
    for m, t, trial in all_jobs:
        jk = job_id(m, t, trial)
        if jk in state["jobs"] and state["jobs"][jk].get("state") == "completed":
            skipped += 1
            continue
        pending.append((m, t, trial))

    total = len(all_jobs)
    if skipped:
        print(f"Skipping {skipped} already-completed jobs")
    print(f"Jobs to run: {len(pending)}/{total}\n")

    if args.dry_run:
        for m, t, trial in pending:
            cwd = os.path.join(exp_dir, m, f"task{t:03d}", f"trial_{trial}")
            print(f"  [{job_id(m,t,trial)}] cd {cwd} && claude --dangerously-skip-permissions \"{CLAUDE_PROMPT}\"")
        return

    if not pending:
        print("All done!")
        return

    # ── Execute ─────────────────────────────────────────────────
    completed = 0
    failed = 0
    lock = threading.Lock()

    def run_and_track(m, t, trial):
        jk = job_id(m, t, trial)
        with lock:
            state["jobs"][jk] = {"state": "running", "method": m, "task": t, "trial": trial}
            save_state(state_path, state)
        result = run_job(m, t, trial, exp_dir)
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
                result = {"state": "failed", "error": str(e), "method": m, "task": t, "trial": trial}

            with lock:
                state["jobs"][jk] = result
                save_state(state_path, state)

            if result.get("state") == "completed":
                completed += 1
            else:
                failed += 1

            print(f"Progress: {completed} done, {failed} failed, "
                  f"{len(pending) - completed - failed} remaining", flush=True)

    print(f"\nRun complete: {completed} done, {failed} failed")
    print(f"Results: {run_dir}")


if __name__ == "__main__":
    main()
