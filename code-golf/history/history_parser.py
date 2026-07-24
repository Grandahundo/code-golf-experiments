#!/usr/bin/env python3
"""
Code Golf History Parser & Benchmark Visualizer
===============================================
Parses Claude Code conversation history (JSONL) for code-golf experiments.

Produces:
  - Best bytes vs cumulative tokens curve
  - Best bytes vs conversation turns curve
  - Improvement efficiency curve
  - Stage breakdown

Verification strategy:
  - Cross-reference version-log.md byte counts with actual .py files
  - Extract verified byte claims from assistant text
  - Sanity-filter: versions with implausibly large jumps (>20%) that are
    not text-verified are treated as broken code and excluded.
"""

import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# ─── Data Structures ───────────────────────────────────────────────

@dataclass
class VersionRecord:
    version_name: str       # e.g. "v8"
    filename: str           # e.g. "v8.py"
    byte_count: int
    history_line: int
    cumulative_tokens: int
    conversation_turn: int
    timestamp: str = ""
    is_verified: bool = False


@dataclass
class Stage:
    name: str
    start_line: int
    end_line: int
    start_turn: int
    end_turn: int
    start_tokens: int
    end_tokens: int
    best_bytes_start: Optional[int]
    best_bytes_end: Optional[int]
    improvement_bytes: int = 0
    description: str = ""


# ─── History Parser ────────────────────────────────────────────────

class HistoryParser:

    def __init__(
        self,
        history_path: str,
        workdir_path: str,
        shared_verified: Optional[Set[int]] = None,
    ):
        self.history_path = Path(history_path)
        self.workdir_path = Path(workdir_path)
        self._trajectory: List[dict] = []
        self._detailed_versions: List[VersionRecord] = []
        self.stages: List[Stage] = []
        self._events: List[dict] = []
        self._verified_byte_counts: Set[int] = set()
        self._shared_verified = shared_verified
        # Subagent tracking
        self._subagent_tokens: Dict[int, int] = {}  # line -> total tokens
        self._total_subagent_tokens: int = 0

    def parse(self) -> None:
        # 1. Collect ground-truth verified byte counts
        self._verified_byte_counts = self._collect_verified_bytes()

        # Merge with shared verified set (from other experiments
        # sharing the same history file)
        if self._shared_verified:
            self._verified_byte_counts |= self._shared_verified

        # 2. Measure actual files
        file_bytes = self._measure_files()

        # 3. Parse JSONL events
        self._events = self._parse_jsonl()

        # 4. Parse subagent histories and map to Agent tool calls
        self._parse_subagents()

        # 5. Build version timeline from Write events
        self._build_version_timeline(file_bytes)

        # 6. Build best-bytes trajectory
        self._build_trajectory()

        # 7. Detect stages
        self._detect_stages()

    def _collect_verified_bytes(self) -> Set[int]:
        """
        Collect verified byte counts from:
        (a) version-log.md files in workdir
        (b) assistant text claims with verification context
        """
        verified = set()

        # (a) From version log files
        if self.workdir_path.exists():
            for logf in self.workdir_path.glob("version*-log.md"):
                try:
                    content = logf.read_text()
                except Exception:
                    continue
                bc_match = re.search(
                    r'\*\*Code-Length:?\*\*\s*\n?\s*(\d+)', content
                )
                if bc_match:
                    bc_val = int(bc_match.group(1))
                    if bc_val < 500:  # skip implausibly large baseline sizes
                        verified.add(bc_val)

        # (b) From assistant text with strong verification signals
        if self.history_path.exists():
            with open(self.history_path, 'r') as fh:
                for line in fh:
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if d.get('type') != 'assistant':
                        continue
                    content = d.get('message', {}).get('content', [])
                    for c in content:
                        if (isinstance(c, dict)
                                and c.get('type') == 'text'):
                            text = c.get('text', '')
                            # Look for patterns like:
                            # "131 bytes and passes all tests"
                            # "verified at 153 bytes"
                            # "best solution is 148 bytes"
                            # "Final best: 116 bytes (v38)"
                            for m in re.finditer(
                                r'(\d{2,4})\s*bytes?\s*(?:and|,)'
                                r'\s*pass(?:es|ing)\s+all\s+tests',
                                text, re.IGNORECASE
                            ):
                                bc_val = int(m.group(1))
                                if bc_val < 500:
                                    verified.add(bc_val)

                            # "Final best: 116 bytes (v38)"
                            # "best solution is 148 bytes"
                            # "verified at 153 bytes"
                            # "HUGE breakthrough — 131 bytes and passes all tests!"
                            # Exclude phrases where THIS number is the baseline/original/target
                            for m in re.finditer(
                                r'(?:final best|best (?:solution|result)|'
                                r'verified|achieved|down to|breakthrough|'
                                r'now at|improved to|currently at)'
                                r'.*?(\d{2,4})\s*bytes?',
                                text, re.IGNORECASE
                            ):
                                bc_val = int(m.group(1))
                                # Must be a plausible code-golf size
                                if bc_val < 50 or bc_val >= 500:
                                    continue
                                # Exclude if THIS number follows baseline/reduction words
                                pre = text[max(0, m.start(1)-30):m.start(1)]
                                if re.search(
                                    r'(?:reduction from|starting from|'
                                    r'original|baseline)\s*$',
                                    pre, re.IGNORECASE
                                ):
                                    continue
                                verified.add(bc_val)

        return verified

    def _measure_files(self) -> Dict[str, int]:
        file_bytes = {}
        if self.workdir_path.exists():
            for f in sorted(self.workdir_path.glob("v*.py")):
                try:
                    file_bytes[f.name] = len(f.read_bytes())
                except Exception:
                    pass
        return file_bytes

    def _parse_jsonl(self) -> List[dict]:
        events = []
        if not self.history_path.exists():
            print(f"  Warning: {self.history_path} not found")
            return events
        with open(self.history_path, 'r') as fh:
            for line_idx, line in enumerate(fh):
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                events.append({
                    'line': line_idx,
                    'type': d.get('type', '?'),
                    'data': d,
                })
        return events

    def _parse_subagents(self) -> None:
        """
        Find subagent JSONL files in the subagents/ directory,
        compute their token usage, and map them to the line in
        the main history where the Agent tool call was made.

        Subagent tokens are credited at the SPAWN point since
        subagents run in parallel with the main thread.
        """
        uuid_dir = self.history_path.parent / self.history_path.stem
        subagents_dir = uuid_dir / 'subagents'
        if not uuid_dir.exists() or not subagents_dir.exists():
            return

        # Build a map: tool_use_id -> total subagent tokens
        id_to_tokens = {}
        for sa_file in subagents_dir.glob("agent-*.jsonl"):
            # Read corresponding meta.json to get toolUseId
            meta_file = subagents_dir / f"{sa_file.stem}.meta.json"
            tool_use_id = None
            agent_desc = ""
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text())
                    tool_use_id = meta.get('toolUseId', '')
                    agent_desc = meta.get('description', '')
                except Exception:
                    pass

            if not tool_use_id:
                continue

            # Count tokens in this subagent's history
            input_tokens = 0
            output_tokens = 0
            try:
                for line in sa_file.read_text().splitlines():
                    if not line.strip():
                        continue
                    try:
                        d = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if d.get('type') == 'assistant':
                        u = d.get('message', {}).get('usage', {})
                        input_tokens += u.get('input_tokens', 0)
                        output_tokens += u.get('output_tokens', 0)
            except Exception:
                pass

            total = input_tokens + output_tokens
            if total > 0:
                id_to_tokens[tool_use_id] = {
                    'tokens': total,
                    'input': input_tokens,
                    'output': output_tokens,
                    'description': agent_desc,
                    'file': sa_file.name,
                }

        # Now find Agent tool calls in the main history and map
        # tool_use IDs to history lines
        for ev in self._events:
            if ev['type'] != 'assistant':
                continue
            content = ev['data'].get('message', {}).get('content', [])
            for c in content:
                if (isinstance(c, dict)
                        and c.get('type') == 'tool_use'
                        and c.get('name') == 'Agent'):
                    tool_id = c.get('id', '')
                    if tool_id in id_to_tokens:
                        info = id_to_tokens[tool_id]
                        self._subagent_tokens[ev['line']] = (
                            self._subagent_tokens.get(ev['line'], 0)
                            + info['tokens']
                        )
                        self._total_subagent_tokens += info['tokens']

    def _build_version_timeline(self, file_bytes: Dict[str, int]) -> None:
        """Walk events, accumulate tokens, record each version file write."""
        # Collect Write events for .py files
        write_events = []
        for ev in self._events:
            if ev['type'] != 'assistant':
                continue
            d = ev['data']
            content = d.get('message', {}).get('content', [])
            for c in content:
                if (isinstance(c, dict)
                        and c.get('type') == 'tool_use'
                        and c.get('name') == 'Write'):
                    inp = c.get('input', {})
                    fp = inp.get('file_path', '')
                    fname = os.path.basename(fp)
                    if re.match(r'v\d+.*\.py', fname):
                        write_events.append({
                            'line': ev['line'],
                            'filename': fname,
                            'timestamp': d.get('timestamp', ''),
                            'content': inp.get('content', ''),
                        })

        # Walk events to accumulate tokens and record versions
        write_idx = 0
        cumulative_tokens = 0
        seen = set()

        for ev in self._events:
            if ev['type'] == 'assistant':
                msg = ev['data'].get('message', {})
                usage = msg.get('usage', {})
                cumulative_tokens += usage.get('input_tokens', 0)
                cumulative_tokens += usage.get('output_tokens', 0)

            # Add subagent tokens at the spawn line
            if ev['line'] in self._subagent_tokens:
                cumulative_tokens += self._subagent_tokens[ev['line']]

            while (write_idx < len(write_events)
                   and write_events[write_idx]['line'] <= ev['line']):
                we = write_events[write_idx]
                fname = we['filename']
                base_match = re.match(r'(v\d+)', fname)
                if base_match:
                    vname = base_match.group(1)
                    if vname not in seen:
                        seen.add(vname)
                        # Byte count: prefer actual file, fall back to
                        # content length
                        if fname in file_bytes:
                            bc = file_bytes[fname]
                        elif we['content']:
                            bc = len(we['content'].encode('utf-8'))
                        else:
                            bc = 0

                        # A version is "verified" if its byte count
                        # matches a known verified count
                        is_verified = bc in self._verified_byte_counts

                        self._detailed_versions.append(VersionRecord(
                            version_name=vname,
                            filename=fname,
                            byte_count=bc,
                            history_line=we['line'],
                            cumulative_tokens=cumulative_tokens,
                            conversation_turn=self._count_turns_before(
                                we['line']
                            ),
                            timestamp=we['timestamp'],
                            is_verified=is_verified,
                        ))
                write_idx += 1

    def _count_turns_before(self, line: int) -> int:
        return sum(1 for ev in self._events
                   if ev['line'] <= line and ev['type'] == 'assistant')

    def _build_trajectory(self) -> None:
        """
        Build monotonically-decreasing best-bytes trajectory.

        Includes ALL versions that improve the best-so-far, marking
        each as verified or unverified.  Verified = byte count confirmed
        by version-log or text claim.
        """
        if not self._detailed_versions:
            return

        sorted_vers = sorted(
            self._detailed_versions, key=lambda v: v.history_line
        )

        best = float('inf')
        for v in sorted_vers:
            bc = v.byte_count
            if bc < 50:
                continue
            if bc < best:
                best = bc
                self._trajectory.append({
                    'version': v.version_name,
                    'bytes': bc,
                    'cumulative_tokens': v.cumulative_tokens,
                    'conversation_turn': v.conversation_turn,
                    'history_line': v.history_line,
                    'is_verified': v.is_verified,
                    'timestamp': v.timestamp,
                })

    def _detect_stages(self) -> None:
        """
        Detect problem-solving stages from trajectory pattern.

        Produces meaningful stages by grouping improvements:
          1. Understanding & First Solution
          2. Algorithm Exploration (big jumps >8%)
          3. Micro-Optimization / Golfing (small jumps)
          4. Converged (final plateau)

        Adjacent improvements of the same type are merged.
        """
        self.stages = []
        if not self._trajectory:
            return

        traj = self._trajectory

        # Stage 1: Understanding → first solution
        first = traj[0]
        self.stages.append(Stage(
            name="1. Understanding & First Solution",
            start_line=0,
            end_line=first['history_line'],
            start_turn=0,
            end_turn=first['conversation_turn'],
            start_tokens=0,
            end_tokens=first['cumulative_tokens'],
            best_bytes_start=None,
            best_bytes_end=first['bytes'],
            improvement_bytes=0,
            description=f"Task exploration → first working solution "
                        f"({first['bytes']} bytes, {first['version']})",
        ))

        if len(traj) < 2:
            return

        # Classify each improvement: "algorithm" (big) or "golfing" (small)
        classified = []
        for i in range(1, len(traj)):
            prev = traj[i - 1]
            curr = traj[i]
            improvement = prev['bytes'] - curr['bytes']
            pct = improvement / prev['bytes'] if prev['bytes'] > 0 else 0
            stage_type = "algorithm" if pct > 0.08 else "golfing"
            classified.append({
                **curr,
                'prev_bytes': prev['bytes'],
                'improvement': improvement,
                'pct': pct,
                'stage_type': stage_type,
            })

        # Build stages by grouping consecutive same-type improvements
        i = 0
        while i < len(classified):
            c = classified[i]
            stage_type = c['stage_type']
            stage_name = (
                "2. Algorithm Exploration"
                if stage_type == "algorithm"
                else "3. Micro-Optimization (Golfing)"
            )

            # Find the end of this group
            j = i
            total_imp = c['improvement']
            start_bytes = c['prev_bytes']
            end_bytes = c['bytes']
            improvements_detail = [f"{c['version']}: -{c['improvement']}B"]

            while j + 1 < len(classified) and classified[j + 1]['stage_type'] == stage_type:
                j += 1
                nc = classified[j]
                total_imp += nc['improvement']
                end_bytes = nc['bytes']
                improvements_detail.append(f"{nc['version']}: -{nc['improvement']}B")

            # Stage spans from the first improvement's line to the last's
            stage_start_line = c['history_line']
            stage_end_line = classified[j]['history_line']
            stage_start_turn = c['conversation_turn']
            stage_end_turn = classified[j]['conversation_turn']
            stage_start_tokens = c['cumulative_tokens']
            stage_end_tokens = classified[j]['cumulative_tokens']

            detail_str = ", ".join(improvements_detail)
            self.stages.append(Stage(
                name=stage_name,
                start_line=stage_start_line,
                end_line=stage_end_line,
                start_turn=stage_start_turn,
                end_turn=stage_end_turn,
                start_tokens=stage_start_tokens,
                end_tokens=stage_end_tokens,
                best_bytes_start=start_bytes,
                best_bytes_end=end_bytes,
                improvement_bytes=total_imp,
                description=f"{-total_imp} bytes total → {end_bytes}B "
                            f"({detail_str})",
            ))

            i = j + 1

    # ─── Public API ──────────────────────────────────────────

    def get_best_bytes_curve(self) -> List[dict]:
        return self._trajectory

    def get_stages(self) -> List[Stage]:
        return self.stages

    def get_all_versions(self) -> List[VersionRecord]:
        return self._detailed_versions

    def get_summary(self) -> dict:
        if not self._trajectory:
            return {}

        first = self._trajectory[0]
        last = self._trajectory[-1]
        total_imp = first['bytes'] - last['bytes']
        total_tokens = last['cumulative_tokens']

        # Compute stages with proper token accounting
        # (tokens between previous stage end and this stage end)
        stages_out = []
        prev_end_tokens = 0
        for s in self.stages:
            tokens_in_stage = s.end_tokens - prev_end_tokens
            prev_end_tokens = s.end_tokens
            stages_out.append({
                'name': s.name,
                'tokens_in_stage': tokens_in_stage,
                'turns': f"{s.start_turn}-{s.end_turn}",
                'improvement': s.improvement_bytes,
            })

        return {
            'initial_bytes': first['bytes'],
            'final_bytes': last['bytes'],
            'total_improvement': total_imp,
            'improvement_pct': round(
                total_imp / first['bytes'] * 100, 1
            ) if first['bytes'] > 0 else 0,
            'total_tokens': total_tokens,
            'total_versions_created': len(self._detailed_versions),
            'total_improvements': len(self._trajectory),
            'bytes_per_token': round(
                total_imp / max(total_tokens, 1), 6
            ),
            'stages': stages_out,
        }

    def print_report(self) -> None:
        s = self.get_summary()
        if not s:
            print("  No data to report.")
            return

        print(f"  Verified byte counts: {sorted(self._verified_byte_counts)}")
        print(f"  Initial bytes:  {s['initial_bytes']}")
        print(f"  Final bytes:    {s['final_bytes']}")
        print(f"  Improvement:    {s['total_improvement']} bytes "
              f"({s['improvement_pct']}%)")
        main_tokens = s['total_tokens'] - self._total_subagent_tokens
        print(f"  Total tokens:   {s['total_tokens']:,}")
        if self._total_subagent_tokens > 0:
            print(f"    (main: {main_tokens:,} + subagents: {self._total_subagent_tokens:,})")
        print(f"  Total versions: {s['total_versions_created']} files, "
              f"{s['total_improvements']} best-improvements")
        print(f"  Efficiency:     {s['bytes_per_token']:.6f} bytes/token")
        print()

        if self.stages:
            print("  STAGES:")
            prev_end = 0
            for st in self.stages:
                imp = f" [-{st.improvement_bytes} bytes]" if st.improvement_bytes > 0 else ""
                tokens_here = st.end_tokens - prev_end
                prev_end = st.end_tokens
                print(f"  {st.name}{imp}")
                print(f"    Turns {st.start_turn}-{st.end_turn}, "
                      f"Tokens: {tokens_here:,}")
                if st.description:
                    print(f"    {st.description[:130]}")

        print(f"\n  BEST-BYTES TRAJECTORY (● verified  ◦ unverified):")
        for tp in self._trajectory:
            marker = "●" if tp.get('is_verified') else "◦"
            label = "" if tp.get('is_verified') else " (unverified)"
            print(f"    {marker} {tp['version']:>6s}: {tp['bytes']:>4d} bytes  "
                  f"@ {tp['cumulative_tokens']:>10,} tokens  "
                  f"(turn {tp['conversation_turn']}){label}")


# ─── Visualization ─────────────────────────────────────────────────

def generate_plots(parsers: Dict[str, HistoryParser], output_dir: str):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not available. pip install matplotlib")
        return

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    EXP_COLORS = {'Baseline': '#3b82f6', 'CoMAP': '#ef4444'}
    STAGE_COLORS = {
        '1. Understanding & First Solution': '#f59e0b',
        '2. Algorithm Exploration': '#3b82f6',
        '3. Micro-Optimization (Golfing)': '#8b5cf6',
        '4. Plateau / Converged': '#ef4444',
    }

    # ─── Figure 1: 2x2 dashboard ───
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Code Golf Benchmark — Experiment Analysis',
                 fontsize=16, fontweight='bold')
    ax1, ax2, ax3, ax4 = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    for exp_name, parser in parsers.items():
        traj = parser.get_best_bytes_curve()
        if not traj:
            continue

        color = EXP_COLORS.get(exp_name, '#6b7280')
        tokens = [t['cumulative_tokens'] for t in traj]
        bytes_vals = [t['bytes'] for t in traj]
        turns = [t['conversation_turn'] for t in traj]
        labels = [t['version'] for t in traj]

        # Split trajectory into verified / unverified for styling
        verified = [(t, b, l) for t, b, l in zip(tokens, bytes_vals, labels)
                    if traj[labels.index(l)].get('is_verified')]
        # Build indices for verified points
        ver_indices = {i for i, t in enumerate(traj) if t.get('is_verified')}

        # Plot 1: Bytes vs Tokens
        # Draw continuous dashed line through all points
        ax1.plot(tokens, bytes_vals, '--', color='#9ca3af', linewidth=1.2,
                 alpha=0.5, zorder=2)
        # Draw verified points as solid filled markers
        ver_tokens = [tokens[i] for i in ver_indices]
        ver_bytes = [bytes_vals[i] for i in ver_indices]
        ver_labels_idx = [i for i in ver_indices]
        ax1.plot(ver_tokens, ver_bytes, '-o', color=color, label=exp_name,
                 linewidth=2.5, markersize=10, markerfacecolor=color,
                 markeredgewidth=1.5, zorder=5)
        # Draw unverified points as hollow gray markers
        unver_indices = [i for i in range(len(traj)) if i not in ver_indices]
        unver_tokens = [tokens[i] for i in unver_indices]
        unver_bytes = [bytes_vals[i] for i in unver_indices]
        if unver_tokens:
            ax1.scatter(unver_tokens, unver_bytes,
                       marker='o', s=70, facecolors='none',
                       edgecolors='#9ca3af', linewidths=1.5,
                       zorder=4, label='_unverified')

        ax1.fill_between(tokens, bytes_vals, alpha=0.08, color=color)

        # Annotate: verified in experiment color, unverified in gray
        for i, (t, b, l) in enumerate(zip(tokens, bytes_vals, labels)):
            c = color if i in ver_indices else '#9ca3af'
            fw = 'bold' if i in ver_indices else 'normal'
            ax1.annotate(l, (t, b), textcoords="offset points",
                        xytext=(0, -15), ha='center', fontsize=7.5,
                        color=c, alpha=0.85, fontweight=fw)

        for s in parser.get_stages():
            sc = STAGE_COLORS.get(s.name, '#6b7280')
            if s.end_tokens > 0:
                ax1.axvline(x=s.end_tokens, color=sc,
                           linestyle='--', alpha=0.3, linewidth=1.2)

        # Plot 2: Bytes vs Turns (same split style)
        ax2.plot(turns, bytes_vals, '--', color='#9ca3af', linewidth=1.2,
                 alpha=0.5, zorder=2)
        ver_turns = [turns[i] for i in ver_indices]
        ax2.plot(ver_turns, ver_bytes, '-s', color=color, label=exp_name,
                 linewidth=2.5, markersize=10, markerfacecolor=color,
                 markeredgewidth=1.5, zorder=5)
        unver_turns = [turns[i] for i in unver_indices]
        if unver_turns:
            ax2.scatter(unver_turns, unver_bytes,
                       marker='s', s=70, facecolors='none',
                       edgecolors='#9ca3af', linewidths=1.5,
                       zorder=4, label='_unverified')
        ax2.fill_between(turns, bytes_vals, alpha=0.08, color=color)
        for i, (t, b, l) in enumerate(zip(turns, bytes_vals, labels)):
            c = color if i in ver_indices else '#9ca3af'
            fw = 'bold' if i in ver_indices else 'normal'
            ax2.annotate(l, (t, b), textcoords="offset points",
                        xytext=(0, -15), ha='center', fontsize=7.5,
                        color=c, alpha=0.85, fontweight=fw)

        # Plot 3: Token accumulation
        ax3.plot(turns, tokens, '-^', color=color, label=exp_name,
                 linewidth=2, markersize=7)

        # Plot 4: Efficiency bars
        efficiencies = []
        for i in range(1, len(traj)):
            dbytes = traj[i-1]['bytes'] - traj[i]['bytes']
            dtokens = (traj[i]['cumulative_tokens']
                       - traj[i-1]['cumulative_tokens'])
            if dtokens > 0 and dbytes > 0:
                efficiencies.append({
                    'label': traj[i]['version'],
                    'efficiency': dbytes / dtokens,
                    'dbytes': dbytes,
                })
        if efficiencies:
            x_pos = range(len(efficiencies))
            eff_values = [e['efficiency'] for e in efficiencies]
            ax4.bar(x_pos, eff_values, color=color, alpha=0.75,
                    label=exp_name, edgecolor='white', linewidth=0.5)
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels(
                [f"{e['label']}\n(-{e['dbytes']}B)"
                 for e in efficiencies],
                fontsize=7.5
            )

    for ax, xlab, ylab, title in [
        (ax1, 'Cumulative Tokens Consumed', 'Best Code Length (bytes)',
         'Best Answer Bytes vs Tokens Consumed'),
        (ax2, 'Conversation Turn', 'Best Code Length (bytes)',
         'Best Answer Bytes vs Conversation Turns'),
    ]:
        ax.set_xlabel(xlab, fontsize=12)
        ax.set_ylabel(ylab, fontsize=12)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.legend(loc='upper right', framealpha=0.9)
        ax.grid(True, alpha=0.25)
        ax.invert_yaxis()

    ax3.set_xlabel('Conversation Turn', fontsize=12)
    ax3.set_ylabel('Cumulative Tokens', fontsize=12)
    ax3.set_title('Token Accumulation Over Turns', fontsize=13, fontweight='bold')
    ax3.legend(loc='lower right', framealpha=0.9)
    ax3.grid(True, alpha=0.25)

    ax4.set_xlabel('Improvement Step', fontsize=12)
    ax4.set_ylabel('Bytes Saved per Token', fontsize=12)
    ax4.set_title('Improvement Efficiency (Δbytes / Δtokens)',
                  fontsize=13, fontweight='bold')
    ax4.legend(loc='upper right', framealpha=0.9)
    ax4.grid(True, alpha=0.25, axis='y')

    plt.tight_layout()
    p1 = out / 'benchmark_curves.png'
    plt.savefig(p1, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {p1}")

    # ─── Figure 2: Stage breakdown ───
    fig2, (ax_s1, ax_s2) = plt.subplots(1, 2, figsize=(16, 5.5))
    fig2.suptitle('Problem-Solving Stage Analysis',
                  fontsize=14, fontweight='bold')

    stage_data = []
    for exp_name, parser in parsers.items():
        for s in parser.get_stages():
            stage_data.append({
                'experiment': exp_name,
                'stage': s.name,
                'short_name': s.name.split('. ')[-1][:25],
                'tokens': s.end_tokens - s.start_tokens,
                'improvement': s.improvement_bytes,
                'turns': s.end_turn - s.start_turn,
                'stage_color': STAGE_COLORS.get(s.name, '#6b7280'),
                'exp_color': EXP_COLORS.get(exp_name, '#6b7280'),
            })

    if stage_data:
        x = np.arange(len(stage_data))
        labels = [f"{d['experiment'][:8]}\n{d['short_name']}"
                  for d in stage_data]

        bars1 = ax_s1.bar(
            x, [d['tokens'] for d in stage_data],
            color=[d['stage_color'] for d in stage_data],
            edgecolor=[d['exp_color'] for d in stage_data],
            linewidth=2.5, alpha=0.85
        )
        ax_s1.set_xticks(x)
        ax_s1.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        ax_s1.set_ylabel('Tokens Consumed', fontsize=12)
        ax_s1.set_title('Token Consumption by Stage', fontsize=13,
                        fontweight='bold')
        ax_s1.grid(True, alpha=0.25, axis='y')

        # Label bars with token counts
        max_tok = max(d['tokens'] for d in stage_data) if stage_data else 1
        for bar, d in zip(bars1, stage_data):
            if d['tokens'] > 0:
                ax_s1.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max_tok * 0.01,
                    f"{d['tokens']:,}",
                    ha='center', va='bottom', fontsize=7,
                    rotation=90, alpha=0.8
                )

        bars2 = ax_s2.bar(
            x, [d['improvement'] for d in stage_data],
            color=[d['stage_color'] for d in stage_data],
            edgecolor=[d['exp_color'] for d in stage_data],
            linewidth=2.5, alpha=0.85
        )
        ax_s2.set_xticks(x)
        ax_s2.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        ax_s2.set_ylabel('Bytes Improved', fontsize=12)
        ax_s2.set_title('Byte Reduction by Stage', fontsize=13,
                        fontweight='bold')
        ax_s2.grid(True, alpha=0.25, axis='y')

        for bar, d in zip(bars2, stage_data):
            if d['improvement'] > 0:
                ax_s2.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() * 1.02,
                    f"-{d['improvement']}",
                    ha='center', va='bottom',
                    fontsize=9, fontweight='bold'
                )

    plt.tight_layout()
    p2 = out / 'stage_analysis.png'
    plt.savefig(p2, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {p2}")


def export_json(parsers: Dict[str, HistoryParser], output_dir: str):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    export = {}
    for name, parser in parsers.items():
        export[name] = {
            'summary': parser.get_summary(),
            'trajectory': parser.get_best_bytes_curve(),
            'stages': [
                {
                    'name': s.name,
                    'start_turn': s.start_turn,
                    'end_turn': s.end_turn,
                    'start_tokens': s.start_tokens,
                    'end_tokens': s.end_tokens,
                    'best_bytes_start': s.best_bytes_start,
                    'best_bytes_end': s.best_bytes_end,
                    'improvement_bytes': s.improvement_bytes,
                    'description': s.description,
                }
                for s in parser.get_stages()
            ],
            'all_versions': [
                {
                    'version': v.version_name,
                    'byte_count': v.byte_count,
                    'history_line': v.history_line,
                    'cumulative_tokens': v.cumulative_tokens,
                    'conversation_turn': v.conversation_turn,
                    'timestamp': v.timestamp,
                    'is_verified': v.is_verified,
                }
                for v in parser.get_all_versions()
            ],
        }

    json_path = out / 'benchmark_data.json'
    with open(json_path, 'w') as f:
        json.dump(export, f, indent=2, default=str)
    print(f"  Exported: {json_path}")


# ─── Main ──────────────────────────────────────────────────────────

def main():
    project_root = Path(__file__).parent.parent
    history_dir = Path(__file__).parent
    from datetime import datetime
    output_dir = history_dir / 'output' / ('run-' + datetime.now().strftime('%Y%m%d-%H%M%S'))

    experiments = [
        {
            'name': 'Baseline',
            'history': (
                history_dir
                / '-Users-jackson-Desktop-code-golf-deepseek-v4-pro-baseline-task004'
                / '841b42b7-cc0b-4b8d-b7c9-401d30acbf88.jsonl'
            ),
            'workdir': (
                project_root / 'deepseek-v4-pro-baseline' / 'task004'
                / 'workdir'
            ),
        },
        {
            'name': 'CoMAP',
            'history': (
                history_dir
                / '-Users-jackson-Desktop-code-golf-deepseek-v4-pro-CoMAP-task004'
                / '3e121c35-394b-4eb6-b472-20cc5495ee60.jsonl'
            ),
            'workdir': (
                project_root / 'deepseek-v4-pro-CoMAP' / 'task004'
                / 'workdir'
            ),
        },
    ]

    import hashlib

    # Detect experiments with identical history files and warn
    history_fingerprints = {}
    for exp in experiments:
        if exp['history'].exists():
            with open(exp['history'], 'rb') as f:
                content_hash = hashlib.md5(f.read(65536)).hexdigest()
            file_size = exp['history'].stat().st_size
            fp = f"{content_hash}_{file_size}"
            if fp in history_fingerprints:
                print(f"\n  ⚠ Warning: '{exp['name']}' history is identical "
                      f"to '{history_fingerprints[fp]}' — "
                      f"experiments should have different histories!")
            else:
                history_fingerprints[fp] = exp['name']

    parsers = {}
    for exp in experiments:
        print(f"\n{'='*60}")
        print(f"  {exp['name']}")
        print(f"{'='*60}")

        if not exp['history'].exists():
            print(f"  SKIP: history not found: {exp['history']}")
            continue

        parser = HistoryParser(
            str(exp['history']),
            str(exp['workdir']),
        )
        parser.parse()
        parsers[exp['name']] = parser
        parser.print_report()

    if parsers:
        print(f"\n{'='*60}")
        print(f"  Generating plots & JSON export")
        print(f"{'='*60}")
        generate_plots(parsers, str(output_dir))
        export_json(parsers, str(output_dir))
        print("\n  ✓ Done! Check history/output/")
    else:
        print("\n  No experiments parsed. Check file paths.")


if __name__ == '__main__':
    main()
