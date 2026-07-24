"""Batch experiment configuration."""

import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BATCH_DIR = os.path.join(PROJECT_ROOT, "batch-experiments")
EXPERIMENTS_DIR = os.path.join(BATCH_DIR, "experiments")
TEMPLATES_DIR = os.path.join(BATCH_DIR, "templates")
RESULTS_DIR = os.path.join(BATCH_DIR, "results")

# ── Experiment matrix ──────────────────────────────────────────
TASKS = list(range(1, 11))  # task001 – task010
TRIALS_PER_COMBO = 3

METHODS = {
    "comap": {
        "label": "CoMAP",
        "color": "#ef4444",
        "has_claude_md": False,
        "has_agent_md": True,
    },
    "comap_claude": {
        "label": "CoMAP+CLAUDE",
        "color": "#dc2626",
        "has_claude_md": True,
        "has_agent_md": True,
    },
    "baseline": {
        "label": "Baseline",
        "color": "#f97316",
        "has_claude_md": False,
        "has_agent_md": True,
    },
    "auto_pal": {
        "label": "auto-PAL",
        "color": "#3b82f6",
        "has_claude_md": True,
        "has_agent_md": True,
    },
    "default": {
        "label": "Default",
        "color": "#10b981",
        "has_claude_md": True,
        "has_agent_md": True,
    },
}

# ── Source directories for task data ────────────────────────────
# gen.py, common.py, verify.py, data.json
TASK_SOURCE_DIR = os.path.join(
    PROJECT_ROOT, "deepseek-v4-pro-baseline"
)

# ── Concurrency ─────────────────────────────────────────────────
MAX_PARALLEL = 8

# ── Claude CLI ──────────────────────────────────────────────────
CLAUDE_BINARY = "claude"
CLAUDE_ARGS = ["--dangerously-skip-permissions"]
CLAUDE_PROMPT = "read agent.md and start working"
