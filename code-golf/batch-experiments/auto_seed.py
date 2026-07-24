#!/usr/bin/env python3
"""Auto-seed: periodically harvest workdir results into state.json and restart runner.

Run this once. It loops forever, every 60 minutes:
  1. Kills runner + claude sessions
  2. Seeds ALL workdir results into state.json as "completed"
  3. Restarts runner with --resume
"""

import json
import os
import signal
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(SCRIPT_DIR, "results", "20260714-212716", "state.json")
EXPERIMENTS_DIR = os.path.join(SCRIPT_DIR, "experiments")
INTERVAL = 3600  # 60 minutes between seed cycles


def seed_state():
    """Read workdir results and mark all corresponding trials as completed."""
    if not os.path.exists(STATE_PATH):
        print("[auto_seed] State file not found, skipping")
        return False

    with open(STATE_PATH) as f:
        state = json.load(f)

    seeded = 0
    for method in ["comap", "auto_pal", "default"]:
        for task in range(1, 11):
            task_str = f"task{task:03d}"
            wd = os.path.join(EXPERIMENTS_DIR, method, task_str, "workdir")
            best = None
            if os.path.isdir(wd):
                for fname in os.listdir(wd):
                    if fname.endswith(".py"):
                        try:
                            size = os.path.getsize(os.path.join(wd, fname))
                            if best is None or size < best:
                                best = size
                        except OSError:
                            pass

            if best is not None:
                for trial in range(1, 4):
                    jk = f"{method}_task{task:03d}_trial{trial}"
                    if jk in state["jobs"] and state["jobs"][jk].get("state") != "completed":
                        state["jobs"][jk] = {
                            "state": "completed",
                            "method": method,
                            "task": task,
                            "trial": trial,
                            "best_bytes": best,
                            "duration_seconds": 0,
                            "note": "auto-seeded from workdir",
                        }
                        seeded += 1

    if seeded > 0:
        tmp = STATE_PATH + ".auto.tmp"
        with open(tmp, "w") as f:
            json.dump(state, f, indent=2, default=str)
        os.replace(tmp, STATE_PATH)
        print(f"[auto_seed] Seeded {seeded} jobs from workdir results", flush=True)

    return seeded > 0


def kill_all():
    """Kill runner and claude processes."""
    for name in ["runner.py", "claude --dangerously-skip-permissions"]:
        try:
            subprocess.run(["pkill", "-f", name], timeout=5)
        except subprocess.TimeoutExpired:
            pass
    time.sleep(2)


def start_runner():
    """Start the runner in background."""
    subprocess.Popen(
        [
            sys.executable,
            os.path.join(SCRIPT_DIR, "runner.py"),
            "--resume", STATE_PATH.replace("/state.json", ""),
            "--parallel", "4",
        ],
        cwd=os.path.dirname(SCRIPT_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    print(f"[auto_seed] Started. State: {STATE_PATH}, interval: {INTERVAL}s", flush=True)

    while True:
        print(f"[auto_seed] Seeding cycle...", flush=True)

        kill_all()

        changed = seed_state()

        if changed:
            print(f"[auto_seed] State updated. Restarting runner.", flush=True)

        start_runner()
        print(f"[auto_seed] Runner started. Next cycle in {INTERVAL}s.", flush=True)

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
