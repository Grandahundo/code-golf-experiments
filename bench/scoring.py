#!/usr/bin/env python3
"""Offline aggregation — compute leaderboard from runs/ directory.

Usage:
    python scoring.py [runs_dir] [--output leaderboard.csv]
"""

import csv
import json
import os
import sys
from collections import defaultdict


def load_all_meta(runs_dir: str) -> list[dict]:
    """Walk runs/ and load every meta.json."""
    metas = []
    for root, dirs, files in os.walk(runs_dir):
        if "meta.json" in files:
            path = os.path.join(root, "meta.json")
            try:
                with open(path) as f:
                    meta = json.load(f)
                metas.append(meta)
            except (json.JSONDecodeError, OSError) as e:
                print(f"  WARNING: could not read {path}: {e}", file=sys.stderr)
    return metas


def build_records(metas: list[dict]) -> dict:
    """Compute pool records (shortest bytes per task across all models/seeds).

    Returns:
        {"task001": {"record_bytes": 62, "record_kaggle": 2438}, ...}
    """
    records = {}
    for m in metas:
        tid = m.get("task_id")
        best = m.get("best_bytes")
        if tid and best is not None:
            if tid not in records or best < records[tid]["record_bytes"]:
                records[tid] = {
                    "record_bytes": best,
                    "record_kaggle": m.get("best_kaggle_score", max(1, 2500 - best)),
                }
    return records


def compute_scores(metas: list[dict], records: dict) -> list[dict]:
    """Compute per-job scores and aggregate."""
    # Per-job rows
    rows = []
    for m in metas:
        tid = m.get("task_id")
        best_bytes = m.get("best_bytes")
        rec = records.get(tid, {})
        record_bytes = rec.get("record_bytes")

        if best_bytes and record_bytes:
            score = record_bytes / best_bytes
        else:
            score = 0.0

        rows.append({
            "task_id": tid,
            "model": m.get("model"),
            "seed": m.get("seed"),
            "finished": m.get("finished", False),
            "rounds_used": m.get("rounds_used", 0),
            "first_correct_round": m.get("first_correct_round"),
            "best_bytes": best_bytes,
            "best_kaggle": m.get("best_kaggle_score"),
            "record_bytes": record_bytes,
            "score": round(score, 4),
            "bytes_curve": m.get("bytes_curve", []),
            "total_tokens": m.get("total_usage", {}).get("total", 0),
            "platform": m.get("platform", "?"),
        })

    return rows


def aggregate_by_model(rows: list[dict]) -> list[dict]:
    """Compute per-model summary stats (best-of-3 and median-of-3)."""
    # Group by (model, task)
    groups = defaultdict(list)
    for r in rows:
        if r["best_bytes"] is not None:
            groups[(r["model"], r["task_id"])].append(r)

    model_task_best = {}
    for (model, tid), entries in groups.items():
        # Best of seeds
        sorted_entries = sorted(entries, key=lambda e: e["best_bytes"])
        best_entry = sorted_entries[0]
        median_entry = sorted_entries[len(sorted_entries) // 2]

        model_task_best[(model, tid)] = {
            "best_of": best_entry,
            "median_of": median_entry,
            "num_seeds": len(entries),
        }

    # Aggregate per model
    model_stats = []
    for model in sorted(set(r["model"] for r in rows)):
        tasks = {tid for m, tid in model_task_best if m == model}
        all_tasks = set(r["task_id"] for r in rows)

        solved_best = sum(
            1 for tid in tasks
            if model_task_best.get((model, tid), {}).get("best_of", {}).get("best_bytes") is not None
        )
        solved_median = sum(
            1 for tid in tasks
            if model_task_best.get((model, tid), {}).get("median_of", {}).get("best_bytes") is not None
        )

        scores_best = [
            model_task_best[(model, tid)]["best_of"]["score"]
            for tid in tasks
            if (model, tid) in model_task_best
        ]
        scores_median = [
            model_task_best[(model, tid)]["median_of"]["score"]
            for tid in tasks
            if (model, tid) in model_task_best
        ]

        first_corrects = [
            mt[(model, tid)]["best_of"]["first_correct_round"]
            for tid in tasks
            if (model, tid) in mt
            and mt[(model, tid)]["best_of"]["first_correct_round"] is not None
        ]

        kaggle_total_best = sum(
            model_task_best[(model, tid)]["best_of"].get("best_kaggle", 0) or 0
            for tid in tasks if (model, tid) in model_task_best
        )

        model_stats.append({
            "model": model,
            "solve_rate_best": round(solved_best / len(all_tasks), 4) if all_tasks else 0,
            "solve_rate_median": round(solved_median / len(all_tasks), 4) if all_tasks else 0,
            "golf_score_best": round(sum(scores_best) / len(all_tasks), 4) if all_tasks else 0,
            "golf_score_median": round(sum(scores_median) / len(all_tasks), 4) if all_tasks else 0,
            "kaggle_total_best": kaggle_total_best,
            "mean_first_correct_round": (
                round(sum(first_corrects) / len(first_corrects), 1)
                if first_corrects else None
            ),
            "tasks_solved_best": solved_best,
            "tasks_total": len(all_tasks),
        })

    return model_stats


def export_leaderboard(model_stats: list[dict], output_path: str):
    """Write leaderboard CSV."""
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "model", "solve_rate_best", "solve_rate_median",
            "golf_score_best", "golf_score_median",
            "kaggle_total_best", "mean_first_correct_round",
            "tasks_solved_best", "tasks_total",
        ])
        writer.writeheader()
        for row in sorted(model_stats, key=lambda r: r["golf_score_best"], reverse=True):
            writer.writerow(row)
    print(f"Leaderboard: {output_path}")


def export_per_task(rows: list[dict], output_path: str):
    """Write per-task detail CSV."""
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "task_id", "model", "seed", "finished", "rounds_used",
            "first_correct_round", "best_bytes", "best_kaggle",
            "record_bytes", "score", "total_tokens", "platform",
        ])
        writer.writeheader()
        for row in sorted(rows, key=lambda r: (r["task_id"], r["model"], r["seed"])):
            writer.writerow(row)
    print(f"Per-task:   {output_path}")


def print_summary(model_stats: list[dict]):
    """Print a human-readable leaderboard."""
    print("\n" + "=" * 80)
    print("Leaderboard (best-of-3 seeds)")
    print("=" * 80)
    header = f"{'Model':<25} {'Solve%':>8} {'Golf':>8} {'Kaggle':>8} {'1st✓':>6} {'Solved':>8}"
    print(header)
    print("-" * 80)
    for row in sorted(model_stats, key=lambda r: r["golf_score_best"], reverse=True):
        print(
            f"{row['model']:<25} "
            f"{row['solve_rate_best']*100:>7.1f}% "
            f"{row['golf_score_best']:>8.4f} "
            f"{row['kaggle_total_best']:>8} "
            f"{row['mean_first_correct_round'] or '-':>6} "
            f"{row['tasks_solved_best']:>4}/{row['tasks_total']:<4}"
        )
    print("=" * 80)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Aggregate code golf benchmark results")
    parser.add_argument("runs_dir", nargs="?", default=None,
                        help="Path to runs/ directory")
    parser.add_argument("--output-dir", "-o", default=None,
                        help="Output directory for CSVs (default: runs_dir)")
    parser.add_argument("--records", default=None,
                        help="Path to records.json (pool records, auto-computed if missing)")
    args = parser.parse_args()

    # Default runs_dir relative to script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    runs_dir = args.runs_dir or os.path.join(script_dir, "runs")

    if not os.path.isdir(runs_dir):
        print(f"Runs directory not found: {runs_dir}")
        sys.exit(1)

    print(f"Scanning: {runs_dir}")
    metas = load_all_meta(runs_dir)
    print(f"  Found {len(metas)} meta.json files")

    if not metas:
        print("No results to aggregate.")
        return

    # Records
    records_path = args.records or os.path.join(runs_dir, "records.json")
    if os.path.exists(records_path):
        with open(records_path) as f:
            records = json.load(f)
        print(f"  Loaded pool records from {records_path}")
    else:
        records = build_records(metas)
        with open(records_path, "w") as f:
            json.dump(records, f, indent=2)
        print(f"  Computed pool records → {records_path}")

    # Compute
    rows = compute_scores(metas, records)
    model_stats = aggregate_by_model(rows)

    # Output
    out_dir = args.output_dir or runs_dir
    os.makedirs(out_dir, exist_ok=True)

    export_leaderboard(model_stats, os.path.join(out_dir, "leaderboard.csv"))
    export_per_task(rows, os.path.join(out_dir, "per_task.csv"))

    print_summary(model_stats)


if __name__ == "__main__":
    main()
