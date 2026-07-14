#!/usr/bin/env python3
"""Watchdog: auto-kill converged Claude Code sessions to keep batch pipeline moving.

Runs alongside runner.py. Checks workdirs every 2 minutes.
If a session hasn't improved its best bytes in CONVERGENCE_MINUTES, kills it.
"""

import json
import os
import signal
import subprocess
import sys
import time
from collections import defaultdict
from typing import Optional

EXPERIMENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiments")
CONVERGENCE_MINUTES = 12  # Kill if no improvement in this many minutes
CHECK_INTERVAL = 120       # Check every 2 minutes

# Track best bytes per pid over time
history: dict = defaultdict(list)  # pid -> [(timestamp, best_bytes), ...]


def get_best_bytes(workdir: str) -> Optional[int]:
    """Smallest .py file in workdir (bytes)."""
    if not os.path.isdir(workdir):
        return None
    best = None
    for fname in os.listdir(workdir):
        if fname.endswith(".py"):
            try:
                size = os.path.getsize(os.path.join(workdir, fname))
                if best is None or size < best:
                    best = size
            except OSError:
                pass
    return best


def get_claude_sessions():
    """Return list of (pid, cwd) for Claude Code sessions."""
    result = []
    try:
        out = subprocess.check_output(
            ["pgrep", "-f", "claude --dangerously-skip-permissions read agent"],
            text=True,
        )
        for pid_str in out.strip().split("\n"):
            if not pid_str:
                continue
            pid = int(pid_str)
            try:
                cwd_out = subprocess.check_output(
                    ["lsof", "-p", str(pid), "-Fn"], text=True, timeout=5
                )
                cwd = None
                lines = cwd_out.split("\n")
                for i, line in enumerate(lines):
                    if line.startswith("fcwd") and i + 1 < len(lines):
                        next_line = lines[i + 1]
                        if next_line.startswith("n"):
                            cwd = next_line[1:].strip()
                            break
                if cwd and "batch-experiments/experiments" in cwd:
                    result.append((pid, cwd))
            except subprocess.CalledProcessError:
                pass
    except subprocess.CalledProcessError:
        pass
    return result


def main():
    print(f"[watchdog] Started. Convergence threshold: {CONVERGENCE_MINUTES}min", flush=True)

    while True:
        sessions = get_claude_sessions()
        now = time.time()

        for pid, cwd in sessions:
            workdir = os.path.join(cwd, "workdir")
            best = get_best_bytes(workdir)

            # Track history
            if pid not in history:
                history[pid] = []
            history[pid].append((now, best))

            # Clean old entries
            cutoff = now - CONVERGENCE_MINUTES * 60
            history[pid] = [(t, b) for t, b in history[pid] if t > cutoff]

            # Check convergence
            if len(history[pid]) >= 3:
                recent_bytes = [b for _, b in history[pid] if b is not None]
                if recent_bytes and all(b == recent_bytes[0] for b in recent_bytes):
                    elapsed = now - history[pid][0][0]
                    if elapsed > CONVERGENCE_MINUTES * 60:
                        task_name = os.path.basename(cwd)
                        method = os.path.basename(os.path.dirname(cwd))
                        print(
                            f"[watchdog] KILLING {method}/{task_name} "
                            f"(PID {pid}, converged at {recent_bytes[0]}B for "
                            f"{elapsed/60:.0f}min)",
                            flush=True,
                        )
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        del history[pid]

        # Print status
        active = len(sessions)
        if active > 0:
            summary = []
            for pid, cwd in sessions:
                task = os.path.basename(cwd)
                workdir = os.path.join(cwd, "workdir")
                best = get_best_bytes(workdir)
                entry = history.get(pid, [])
                # Time since best bytes last improved
                stale = 0
                if entry and best is not None:
                    prev_bytes = None
                    last_change = now
                    for t, b in sorted(entry):
                        if b is not None and b != prev_bytes:
                            last_change = t
                            prev_bytes = b
                    stale = (now - last_change) / 60
                summary.append(f"{task}={best}B(no_imprv{stale:.0f}m)")
            print(f"[watchdog] {active} sessions: {', '.join(summary)}", flush=True)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
