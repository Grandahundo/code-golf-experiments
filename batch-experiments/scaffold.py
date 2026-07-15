#!/usr/bin/env python3
"""Scaffold experiment directories for batch code-golf runs.

Creates:  batch-experiments/experiments/<method>/task<NNN>/
Populates with agent.md, CLAUDE.md, gen.py, verify.py, common.py, data.json
"""

import os
import shutil
import sys

# ── Paths (relative to this script) ────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
EXPERIMENTS_DIR = os.path.join(SCRIPT_DIR, "experiments")

# Source for per-task data files
TASK_SOURCE_DIR = os.path.join(
    PROJECT_ROOT, "deepseek-v4-pro-baseline"
)

# ── Methods definition ─────────────────────────────────────────
METHODS = {
    "comap": {
        "label": "CoMAP",
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

# ── Per-task files copied as-is from source task directories ──
COPY_FROM_SOURCE = ["gen.py", "common.py", "verify.py", "data.json"]


def render_template(template_path: str, task_num: int) -> str:
    """Read template and substitute {{TASK_NUM}} placeholder."""
    with open(template_path, "r") as f:
        content = f.read()
    return content.replace("{{TASK_NUM}}", f"{task_num:03d}")


def scaffold_method_task(method: str, task_num: int, force: bool = False):
    """Create one (method, task) experiment directory."""
    task_str = f"task{task_num:03d}"
    target_dir = os.path.join(EXPERIMENTS_DIR, method, task_str)

    # Skip if already complete
    workdir = os.path.join(target_dir, "workdir")
    agent_md_path = os.path.join(target_dir, "agent.md")
    if os.path.exists(agent_md_path) and not force:
        print(f"  [skip] {method}/{task_str} — already exists")
        return

    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(workdir, exist_ok=True)

    meta = METHODS[method]

    # ── Write agent.md from template ──
    if meta["has_agent_md"]:
        template = os.path.join(TEMPLATES_DIR, method, "agent.md")
        if os.path.exists(template):
            content = render_template(template, task_num)
            with open(agent_md_path, "w") as f:
                f.write(content)

    # ── Write CLAUDE.md from template ──
    if meta["has_claude_md"]:
        template = os.path.join(TEMPLATES_DIR, method, "CLAUDE.md")
        if os.path.exists(template):
            content = render_template(template, task_num)
            claude_path = os.path.join(target_dir, "CLAUDE.md")
            with open(claude_path, "w") as f:
                f.write(content)

    # ── Copy task-specific data files ──
    source_task_dir = os.path.join(TASK_SOURCE_DIR, task_str)
    for filename in COPY_FROM_SOURCE:
        src = os.path.join(source_task_dir, filename)
        dst = os.path.join(target_dir, filename)
        if os.path.exists(src):
            shutil.copy2(src, dst)
        else:
            print(f"  [warn] {method}/{task_str}: {filename} not found in {source_task_dir}")

    print(f"  [done] {method}/{task_str}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Scaffold batch experiment directories")
    parser.add_argument(
        "--tasks", type=str, default="1-10",
        help="Task range, e.g. '1-5' or '1,3,5' (default: 1-10)"
    )
    parser.add_argument(
        "--methods", type=str, default="comap,auto_pal,default",
        help="Comma-separated methods (default: comap,auto_pal,default)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite existing directories"
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

    # Validate
    for m in methods:
        if m not in METHODS:
            print(f"Unknown method: {m}. Choices: {list(METHODS.keys())}")
            sys.exit(1)

    print(f"Scaffolding {len(tasks)} tasks × {len(methods)} methods "
          f"= {len(tasks) * len(methods)} directories")
    print(f"Output: {EXPERIMENTS_DIR}\n")

    for method in methods:
        print(f"[{method}]")
        for task_num in tasks:
            scaffold_method_task(method, task_num, force=args.force)
        print()

    print("Done. Run with --force to overwrite existing directories.")


if __name__ == "__main__":
    main()
