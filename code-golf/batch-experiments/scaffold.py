#!/usr/bin/env python3
"""Scaffold per-trial experiment directories for a batch run.

Creates:  runs/<timestamp>/experiments/<method>/task<NNN>/trial_<N>/
Each trial gets its OWN copy of all files + workdir — truly independent.
"""

import os
import shutil
import sys
from datetime import datetime

# ── Paths ──────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
RUNS_DIR = os.path.join(SCRIPT_DIR, "runs")

# Source for per-task data files (gen.py, verify.py, etc.)
TASK_SOURCE_DIR = os.path.join(PROJECT_ROOT, "deepseek-v4-pro-baseline")

# ── Methods definition ─────────────────────────────────────────
METHODS = {
    "comap": {
        "label": "CoMAP",
        "has_claude_md": False,
        "has_agent_md": True,
    },
    "comap_claude": {
        "label": "CoMAP+CLAUDE",
        "has_claude_md": True,
        "has_agent_md": True,
    },
    "baseline": {
        "label": "Baseline",
        "has_claude_md": False,
        "has_agent_md": True,
    },
    "auto_pal": {
        "label": "auto-PAL",
        "has_claude_md": True,
        "has_agent_md": True,
    },
    "default": {
        "label": "Default",
        "has_claude_md": True,
        "has_agent_md": True,
    },
}

COPY_FROM_SOURCE = ["gen.py", "common.py", "verify.py", "data.json"]


def render_template(template_path: str, task_num: int) -> str:
    with open(template_path, "r") as f:
        return f.read().replace("{{TASK_NUM}}", f"{task_num:03d}")


def scaffold_run(methods: list, tasks: list, trials: int = 3) -> str:
    """Create a new timestamped run directory with all experiment files.

    Returns the run directory path.
    """
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = os.path.join(RUNS_DIR, ts)
    exp_dir = os.path.join(run_dir, "experiments")
    os.makedirs(exp_dir, exist_ok=True)

    total = len(methods) * len(tasks) * trials
    print(f"Scaffolding run: {run_dir}")
    print(f"  {len(methods)} methods × {len(tasks)} tasks × {trials} trials = {total} dirs\n")

    for method in methods:
        meta = METHODS[method]
        for task_num in tasks:
            task_str = f"task{task_num:03d}"
            source_task_dir = os.path.join(TASK_SOURCE_DIR, task_str)

            for trial in range(1, trials + 1):
                trial_dir = os.path.join(exp_dir, method, task_str, f"trial_{trial}")
                workdir = os.path.join(trial_dir, "workdir")
                os.makedirs(workdir, exist_ok=True)

                # ── agent.md ──
                if meta["has_agent_md"]:
                    tmpl = os.path.join(TEMPLATES_DIR, method, "agent.md")
                    if os.path.exists(tmpl):
                        with open(os.path.join(trial_dir, "agent.md"), "w") as f:
                            f.write(render_template(tmpl, task_num))

                # ── CLAUDE.md ──
                if meta["has_claude_md"]:
                    tmpl = os.path.join(TEMPLATES_DIR, method, "CLAUDE.md")
                    if os.path.exists(tmpl):
                        with open(os.path.join(trial_dir, "CLAUDE.md"), "w") as f:
                            f.write(render_template(tmpl, task_num))

                # ── Task data files ──
                for filename in COPY_FROM_SOURCE:
                    src = os.path.join(source_task_dir, filename)
                    dst = os.path.join(trial_dir, filename)
                    if os.path.exists(src):
                        shutil.copy2(src, dst)

        print(f"  [{method}] {len(tasks)} tasks × {trials} trials")

    print(f"\nDone: {run_dir}")
    return run_dir


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Scaffold batch experiment directories")
    parser.add_argument("--tasks", type=str, default="1-10")
    parser.add_argument("--methods", type=str, default="comap,comap_claude,baseline,auto_pal,default")
    parser.add_argument("--trials", type=int, default=3)
    args = parser.parse_args()

    tasks = []
    for part in args.tasks.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            tasks.extend(range(int(lo), int(hi) + 1))
        else:
            tasks.append(int(part))

    methods = [m.strip() for m in args.methods.split(",")]
    for m in methods:
        if m not in METHODS:
            print(f"Unknown method: {m}. Choices: {list(METHODS.keys())}")
            sys.exit(1)

    scaffold_run(methods, tasks, args.trials)


if __name__ == "__main__":
    main()
