#!/usr/bin/env python3
"""批量 code golf 实验：96 任务 × 5 模型 × 3 seeds，支持并行。

用法:
    python batch_run.py --models deepseek-v4-pro                    # 单模型全任务
    python batch_run.py --models deepseek-v4-pro --workers 8        # 8 并行
    python batch_run.py --tasks 256,214 --models qwen3.7-max        # 指定任务
    python batch_run.py --dry-run                                   # 只看矩阵
"""

import argparse
import json
import os
import sys
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from run import run, API_CONFIGS


def load_task_ids(xlsx_path: str) -> list[str]:
    df = pd.read_excel(xlsx_path, sheet_name="选定100题", header=1)
    return [str(int(t)) for t in df["题号"].tolist()]


def run_one(tid: str, mid: str, seed: int, rounds: int, output_dir: str,
            idx: int, total: int, lock: threading.Lock) -> dict:
    """跑单个 job，写结果文件。返回统计 dict。"""
    ts = time.strftime("%Y%m%d_%H%M%S")
    fname = f"{mid}_task{tid}_seed{seed}_{ts}.json"
    out_path = os.path.join(output_dir, fname)

    if os.path.exists(out_path):
        with lock:
            print(f"[{idx}/{total}] ⏭️  {mid} task{tid} seed{seed} — skip")
        return {"skipped": True}

    t0 = time.time()
    try:
        result = run(f"task{tid}", rounds, mid, seed)
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False, default=str)

        elapsed = time.time() - t0
        solved = "✅" if result["solved"] else "❌"
        best = result["bytes"] if result["bytes"] else "-"
        with lock:
            print(f"[{idx}/{total}] {solved} {mid} task{tid} seed{seed}  "
                  f"{best}B ({elapsed:.0f}s)")

        return {"solved": result["solved"], "bytes": result["bytes"]}

    except Exception as e:
        elapsed = time.time() - t0
        with lock:
            print(f"[{idx}/{total}] 💥 {mid} task{tid} seed{seed}  "
                  f"{e} ({elapsed:.0f}s)")
        return {"failed": True}


def main():
    parser = argparse.ArgumentParser(description="Batch code golf experiment")
    parser.add_argument("--tasks", default=None,
                        help="Comma-separated task IDs (default: all 96)")
    parser.add_argument("--models", default=None,
                        help="Comma-separated model keys (default: all 5)")
    parser.add_argument("--seeds", type=int, default=3,
                        help="Seeds per (task, model) (default: 3)")
    parser.add_argument("--rounds", type=int, default=30)
    parser.add_argument("--workers", type=int, default=4,
                        help="Parallel workers (default: 4)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    # ── 任务 ────────────────────────────────────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))
    xlsx_path = os.path.join(script_dir, "..", "..", "benchmark_1_3_2_selection.xlsx")
    if args.tasks:
        task_ids = [t.strip() for t in args.tasks.split(",")]
    else:
        task_ids = load_task_ids(xlsx_path)

    # ── 模型 ────────────────────────────────────────────────────────
    if args.models:
        model_keys = [m.strip() for m in args.models.split(",")]
        for m in model_keys:
            if m not in API_CONFIGS:
                print(f"Unknown model: {m}. Options: {list(API_CONFIGS)}")
                sys.exit(1)
    else:
        model_keys = list(API_CONFIGS.keys())

    seeds = list(range(1, args.seeds + 1))
    output_dir = args.output_dir or os.path.join(script_dir, "results")
    os.makedirs(output_dir, exist_ok=True)

    jobs = [(tid, mid, seed) for tid in task_ids
            for mid in model_keys for seed in seeds]

    print(f"Tasks:   {len(task_ids)} ({task_ids[0]}..{task_ids[-1]})")
    print(f"Models:  {model_keys}")
    print(f"Seeds:   {args.seeds}")
    print(f"Workers: {args.workers}")
    print(f"Total:   {len(jobs)} jobs")
    print(f"Output:  {output_dir}")
    print()

    if args.dry_run:
        return

    # ── 并行跑 ──────────────────────────────────────────────────────
    t_start = time.time()
    lock = threading.Lock()
    total = len(jobs)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {}
        for i, (tid, mid, seed) in enumerate(jobs, 1):
            fut = pool.submit(run_one, tid, mid, seed, args.rounds,
                              output_dir, i, total, lock)
            futures[fut] = (tid, mid, seed)

        solved_count = 0
        failed_count = 0
        skipped_count = 0

        for fut in as_completed(futures):
            r = fut.result()
            if r.get("skipped"):
                skipped_count += 1
            elif r.get("failed"):
                failed_count += 1
            elif r.get("solved"):
                solved_count += 1

    # ── 汇总 ──────────────────────────────────────────────────────────
    total_elapsed = time.time() - t_start
    completed = total - skipped_count
    print()
    print("=" * 60)
    print(f"Completed: {completed}/{total} ({skipped_count} skipped)")
    print(f"Solved:    {solved_count}/{completed} jobs")
    print(f"Failed:    {failed_count}")
    print(f"Time:      {total_elapsed:.0f}s ({total_elapsed/60:.1f}m)")
    print(f"Output:    {output_dir}")


if __name__ == "__main__":
    main()
