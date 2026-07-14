#!/usr/bin/env python3
"""Aggregate results across multiple trials per (method, task) combo.

Reads state.json from a runner output directory, parses each trial's
workdir to extract byte counts, and computes per-combo statistics.
"""

import json
import os
import statistics
import sys
from collections import defaultdict

# ── Import HistoryParser from the parent project ───────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "history"))

from history_parser import HistoryParser  # type: ignore


def compute_stats(values: list) -> dict:
    """Compute summary statistics for a list of numeric values."""
    if not values:
        return {"count": 0, "min": None, "max": None,
                "mean": None, "median": None, "std": None}
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": round(statistics.mean(values), 1),
        "median": round(statistics.median(values), 1),
        "std": round(statistics.stdev(values), 1) if len(values) >= 2 else 0,
    }


def aggregate(run_dir: str) -> dict:
    """Aggregate results from a completed (or partial) batch run."""
    state_path = os.path.join(run_dir, "state.json")
    if not os.path.exists(state_path):
        print(f"State file not found: {state_path}")
        sys.exit(1)

    with open(state_path, "r") as f:
        state = json.load(f)

    # Group jobs by (method, task)
    groups = defaultdict(list)
    for job_key, job in state.get("jobs", {}).items():
        if job.get("state") != "completed":
            continue
        method = job.get("method", "?")
        task = job.get("task", 0)
        groups[(method, task)].append(job)

    # Compute per-group stats
    aggregated = {}
    for (method, task), jobs in sorted(groups.items()):
        task_str = f"task{task:03d}"
        byte_values = [j.get("best_bytes") for j in jobs
                       if j.get("best_bytes") is not None]
        duration_values = [j.get("duration_seconds", 0) for j in jobs]

        entry = {
            "method": method,
            "task": task,
            "task_str": task_str,
            "trials_completed": len(jobs),
            "best_bytes": compute_stats(byte_values),
            "duration_seconds": compute_stats(duration_values),
            "best_trial": min(jobs, key=lambda j: j.get("best_bytes", float("inf")))
            if byte_values else None,
        }
        aggregated[f"{method}_{task_str}"] = entry

    return {
        "run_id": state.get("run_id", os.path.basename(run_dir)),
        "aggregated_at": state.get("updated_at", ""),
        "total_jobs": len(state.get("jobs", {})),
        "completed_jobs": len([j for j in state.get("jobs", {}).values()
                               if j.get("state") == "completed"]),
        "results": aggregated,
    }


def print_summary(aggregated: dict):
    """Print a human-readable summary table."""
    results = aggregated.get("results", {})

    # By method
    print("=" * 80)
    print("Per-Method Summary")
    print("=" * 80)
    methods = sorted(set(r["method"] for r in results.values()))
    for method in methods:
        entries = [e for e in results.values() if e["method"] == method]
        all_bytes = []
        for e in entries:
            if e["best_bytes"]["min"] is not None:
                all_bytes.append(e["best_bytes"]["min"])
        tasks_done = len([e for e in entries if e["trials_completed"] > 0])
        if all_bytes:
            print(f"  {method}: {tasks_done} tasks, "
                  f"best overall={min(all_bytes)}B, "
                  f"mean best={statistics.mean(all_bytes):.0f}B")
        else:
            print(f"  {method}: no results yet")

    print()
    print("=" * 80)
    print("Per-Task Leaderboard")
    print("=" * 80)

    tasks = sorted(set(r["task"] for r in results.values()))
    for task in tasks:
        task_str = f"task{task:03d}"
        print(f"\n  [{task_str}]")
        entries = sorted(
            [e for e in results.values() if e["task"] == task],
            key=lambda e: e["best_bytes"].get("min", float("inf"))
        )
        for e in entries:
            bs = e["best_bytes"]
            status = f"min={bs['min']}B, mean={bs['mean']}B, std=±{bs['std']}B" if bs["count"] > 0 else "no data"
            print(f"    {e['method']}: {status} (n={bs['count']})")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Aggregate batch experiment results"
    )
    parser.add_argument(
        "run_dir",
        help="Path to the run directory (e.g., results/20260714-120000)"
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="Output JSON path (default: <run_dir>/aggregated.json)"
    )
    parser.add_argument(
        "--summary-only", action="store_true",
        help="Only print summary, don't save JSON"
    )
    args = parser.parse_args()

    run_dir = os.path.abspath(args.run_dir)
    aggregated = aggregate(run_dir)

    if not args.summary_only:
        output_path = args.output or os.path.join(run_dir, "aggregated.json")
        with open(output_path, "w") as f:
            json.dump(aggregated, f, indent=2, default=str)
        print(f"Saved: {output_path}")
        print()

    print_summary(aggregated)


if __name__ == "__main__":
    main()
