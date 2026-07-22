#!/usr/bin/env python3
"""Validate task JSON files — scan schema, value ranges, gen.py coverage.

Usage: python validate_tasks.py [--tasks-dir PATH] [--gen-dir PATH]
"""

import json
import os
import sys
from collections import Counter

# Allow running from bench/ or project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from task_loader import grid_area, load_task


def scan_tasks(tasks_dir: str, gen_dir: str) -> dict:
    """Scan all task files and return a report dict."""
    files = sorted(
        f for f in os.listdir(tasks_dir) if f.startswith("task") and f.endswith(".json")
    )

    report = {
        "total_files": len(files),
        "schema": Counter(),         # top-level keys seen
        "train_counts": [],
        "test_counts": [],
        "arc_gen_counts": [],
        "grid_areas": [],
        "value_set": set(),
        "has_gen": 0,
        "missing_gen": [],
        "gen_lengths": [],
        "parse_errors": [],
    }

    for fname in files:
        path = os.path.join(tasks_dir, fname)
        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            report["parse_errors"].append((fname, str(e)))
            continue

        # Schema keys
        report["schema"].update(data.keys())

        # Example counts
        for split in ("train", "test", "arc-gen"):
            examples = data.get(split, [])
            count = len(examples)
            report[f"{split.replace('-', '_')}_counts"].append(count)

            # Values & areas
            for ex in examples:
                for grid_key in ("input", "output"):
                    grid = ex.get(grid_key, [])
                    if isinstance(grid, list):
                        for row in grid:
                            if isinstance(row, list):
                                report["value_set"].update(row)
                        if grid_key == "input" and isinstance(grid, list) and len(grid) > 0:
                            area = len(grid) * (len(grid[0]) if isinstance(grid[0], list) else 1)
                            report["grid_areas"].append(area)

        # gen.py
        task_id = fname.replace(".json", "")
        gen_path = os.path.join(gen_dir, task_id, "gen.py")
        if os.path.exists(gen_path):
            report["has_gen"] += 1
            report["gen_lengths"].append(os.path.getsize(gen_path))
        else:
            report["missing_gen"].append(task_id)

    return report


def print_report(report: dict):
    """Pretty-print the validation report."""
    print("=" * 60)
    print("Task Validation Report")
    print("=" * 60)

    n = report["total_files"]
    print(f"\nTotal files found: {n}")

    if report["parse_errors"]:
        print(f"\n⚠️  Parse errors ({len(report['parse_errors'])}):")
        for fname, err in report["parse_errors"][:10]:
            print(f"  {fname}: {err}")
        if len(report["parse_errors"]) > 10:
            print(f"  ... and {len(report['parse_errors']) - 10} more")

    # Schema
    print(f"\nTop-level keys: {dict(report['schema'])}")

    # Counts
    for split in ("train", "test", "arc_gen"):
        counts = report[f"{split}_counts"]
        if counts:
            print(f"\n{split} examples per task:")
            print(f"  min={min(counts)}, max={max(counts)}, "
                  f"mean={sum(counts)/len(counts):.1f}, median={sorted(counts)[len(counts)//2]}")

    # Grid areas
    areas = report["grid_areas"]
    if areas:
        sorted_areas = sorted(areas)
        print(f"\nGrid areas (rows × cols):")
        print(f"  min={min(areas)}, max={max(areas)}, "
              f"mean={sum(areas)/len(areas):.1f}, median={sorted_areas[len(sorted_areas)//2]}")
        # percentile distribution
        for pct in (25, 50, 75, 90, 95, 99):
            idx = min(int(len(sorted_areas) * pct / 100), len(sorted_areas) - 1)
            print(f"  p{pct}: {sorted_areas[idx]}")

    # Values
    vals = sorted(report["value_set"])
    print(f"\nUnique cell values: {vals}")
    if vals and (min(vals) < 0 or max(vals) > 9):
        print("  ⚠️  Values fall outside 0-9 range!")
    else:
        print("  ✓ All values in 0-9 range")

    # gen.py coverage
    print(f"\ngen.py coverage: {report['has_gen']}/{n} tasks")
    if report["missing_gen"]:
        print(f"  Missing: {len(report['missing_gen'])} tasks")
        if len(report['missing_gen']) <= 20:
            print(f"  IDs: {', '.join(report['missing_gen'])}")
        else:
            print(f"  First 20: {', '.join(report['missing_gen'][:20])}")

    if report["gen_lengths"]:
        gl = report["gen_lengths"]
        print(f"  gen.py sizes: min={min(gl)}, max={max(gl)}, mean={sum(gl)/len(gl):.0f} bytes")

    print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate code golf task files")
    parser.add_argument("--tasks-dir", default=None,
                        help="Path to task JSON directory")
    parser.add_argument("--gen-dir", default=None,
                        help="Path to gen.py directory")
    args = parser.parse_args()

    # Default paths relative to bench/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tasks_dir = args.tasks_dir or os.path.join(script_dir, "..", "code-golf", "google-code-golf-2025")
    gen_dir = args.gen_dir or os.path.join(script_dir, "..", "code-golf", "deepseek-v4-pro-baseline")

    # Resolve
    tasks_dir = os.path.abspath(tasks_dir)
    gen_dir = os.path.abspath(gen_dir)

    if not os.path.isdir(tasks_dir):
        print(f"Tasks directory not found: {tasks_dir}")
        sys.exit(1)

    print(f"Tasks dir: {tasks_dir}")
    print(f"Gen dir:   {gen_dir}")
    print()

    report = scan_tasks(tasks_dir, gen_dir)
    print_report(report)

    # Exit non-zero if issues found
    if report["parse_errors"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
