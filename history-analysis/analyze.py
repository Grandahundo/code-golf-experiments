#!/usr/bin/env python3
"""
History Analysis — Claude Experiment 综合分析
==============================================
解析 history-analysis 中所有 task 的 JSONL 对话历史，
借鉴 history/history_parser.py 的方法论，
输出每个 task 的：
  - 版本迭代轨迹（bytes vs tokens vs turns）
  - 各阶段 token 消耗与效率
  - 跨 task 对比汇总
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
    version_name: str
    filename: str
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

    def __init__(self, history_path: str, workdir_path: str):
        self.history_path = Path(history_path)
        self.workdir_path = Path(workdir_path)
        self._trajectory: List[dict] = []
        self._detailed_versions: List[VersionRecord] = []
        self.stages: List[Stage] = []
        self._events: List[dict] = []
        self._verified_byte_counts: Set[int] = set()
        self._subagent_tokens: Dict[int, int] = {}
        self._total_subagent_tokens: int = 0

    def parse(self) -> None:
        self._verified_byte_counts = self._collect_verified_bytes()
        file_bytes = self._measure_files()
        self._events = self._parse_jsonl()
        self._parse_subagents()
        self._build_version_timeline(file_bytes)
        self._build_trajectory()
        self._detect_stages()

    def _collect_verified_bytes(self) -> Set[int]:
        """从对话文本中提取被验证过的 byte 数"""
        verified = set()
        if not self.history_path.exists():
            return verified

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
                    if isinstance(c, dict) and c.get('type') == 'text':
                        text = c.get('text', '')
                        # "X bytes and passes all tests"
                        for m in re.finditer(
                            r'(\d{2,4})\s*bytes?\s*(?:and|,)\s*pass(?:es|ing)?\s+all\s+tests',
                            text, re.IGNORECASE
                        ):
                            bc = int(m.group(1))
                            if bc < 500:
                                verified.add(bc)
                        # "best: Xb" / "verified at X bytes"
                        for m in re.finditer(
                            r'(?:best|verified|achieved|down to|now at|'
                            r'improved to|currently at|final).*?(\d{2,4})\s*b',
                            text, re.IGNORECASE
                        ):
                            bc = int(m.group(1))
                            if 20 <= bc < 500:
                                verified.add(bc)
                        # "best:229b" / "best: 116 bytes"
                        for m in re.finditer(
                            r'best\s*:\s*(\d{2,4})\s*b',
                            text, re.IGNORECASE
                        ):
                            bc = int(m.group(1))
                            if bc < 500:
                                verified.add(bc)
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
        """解析 subagent 的 token 消耗"""
        uuid_dir = self.history_path.parent / self.history_path.stem
        subagents_dir = uuid_dir / 'subagents'
        if not uuid_dir.exists() or not subagents_dir.exists():
            return

        id_to_tokens = {}
        for sa_file in subagents_dir.glob("agent-*.jsonl"):
            meta_file = subagents_dir / f"{sa_file.stem}.meta.json"
            tool_use_id = None
            if meta_file.exists():
                try:
                    meta = json.loads(meta_file.read_text())
                    tool_use_id = meta.get('toolUseId', '')
                except Exception:
                    pass
            if not tool_use_id:
                continue

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
                }

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
        write_events = []
        for ev in self._events:
            if ev['type'] != 'assistant':
                continue
            d = ev['data']
            content = d.get('message', {}).get('content', [])
            for c in content:
                if (isinstance(c, dict)
                        and c.get('type') == 'tool_use'
                        and c.get('name') in ('Write', 'Bash')):
                    inp = c.get('input', {})
                    # Write events
                    fp = inp.get('file_path', '')
                    fname = os.path.basename(fp)
                    if re.match(r'v\d+.*\.py', fname):
                        write_events.append({
                            'line': ev['line'],
                            'filename': fname,
                            'timestamp': d.get('timestamp', ''),
                            'content': inp.get('content', ''),
                        })
                    # Bash redirect events: "cat > workdir/vN.py <<'EOF'"
                    # or "printf '...' > workdir/vN.py"
                    cmd = inp.get('command', '')
                    for m in re.finditer(
                        r'(?:cat|printf)\s.*?>\s*(?:.*?/)?(v\d+.*?\.py)\b',
                        cmd
                    ):
                        fname = m.group(1)
                        content_str = ''
                        # extract content from heredoc: cat > file <<'EOF'\n...\nEOF
                        heredoc_match = re.search(
                            r"<<'EOF'\n(.*?)\nEOF", cmd, re.DOTALL
                        )
                        if heredoc_match:
                            content_str = heredoc_match.group(1)
                        else:
                            # extract content from printf '...' > file
                            printf_match = re.search(
                                r"printf\s+'(.*)'\s*>", cmd
                            )
                            if printf_match:
                                content_str = printf_match.group(1)
                        write_events.append({
                            'line': ev['line'],
                            'filename': fname,
                            'timestamp': d.get('timestamp', ''),
                            'content': content_str,
                        })

        write_idx = 0
        cumulative_tokens = 0
        seen = set()

        for ev in self._events:
            if ev['type'] == 'assistant':
                msg = ev['data'].get('message', {})
                usage = msg.get('usage', {})
                cumulative_tokens += usage.get('input_tokens', 0)
                cumulative_tokens += usage.get('output_tokens', 0)

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
                        if fname in file_bytes:
                            bc = file_bytes[fname]
                        elif we['content']:
                            bc = len(we['content'].encode('utf-8'))
                        else:
                            bc = 0

                        is_verified = bc in self._verified_byte_counts

                        self._detailed_versions.append(VersionRecord(
                            version_name=vname,
                            filename=fname,
                            byte_count=bc,
                            history_line=we['line'],
                            cumulative_tokens=cumulative_tokens,
                            conversation_turn=self._count_turns_before(we['line']),
                            timestamp=we['timestamp'],
                            is_verified=is_verified,
                        ))
                write_idx += 1

    def _count_turns_before(self, line: int) -> int:
        return sum(1 for ev in self._events
                   if ev['line'] <= line and ev['type'] == 'assistant')

    def _build_trajectory(self) -> None:
        if not self._detailed_versions:
            return

        sorted_vers = sorted(self._detailed_versions, key=lambda v: v.history_line)
        best = float('inf')
        for v in sorted_vers:
            bc = v.byte_count
            if bc < 20:
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
        self.stages = []
        if not self._trajectory:
            return

        traj = self._trajectory
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

        # Classify improvements
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

        i = 0
        while i < len(classified):
            c = classified[i]
            stage_type = c['stage_type']
            stage_name = (
                "2. Algorithm Exploration"
                if stage_type == "algorithm"
                else "3. Micro-Optimization (Golfing)"
            )

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
                description=f"{-total_imp} bytes total → {end_bytes}B ({detail_str})",
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


# ─── Cross-Task Analysis ──────────────────────────────────────────

def cross_task_summary(parsers: Dict[str, HistoryParser]) -> None:
    """跨 task 对比分析"""
    print("\n" + "=" * 80)
    print("  CROSS-TASK COMPARISON")
    print("=" * 80)

    rows = []
    for task_name, parser in parsers.items():
        s = parser.get_summary()
        if not s:
            rows.append([task_name, '-', '-', '-', '-', '-', '-'])
            continue
        rows.append([
            task_name,
            f"{s['initial_bytes']}B",
            f"{s['final_bytes']}B",
            f"-{s['total_improvement']}B ({s['improvement_pct']}%)",
            f"{s['total_tokens']:,}",
            f"{s['total_versions_created']}",
            f"{s['bytes_per_token']:.4f}",
        ])

    # Header
    headers = ["Task", "Start", "Best", "Improvement", "Tokens", "Versions", "B/token"]
    col_widths = [10, 8, 8, 18, 12, 10, 10]
    fmt = "  ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    print(f"  {fmt}")
    print(f"  {'-' * (sum(col_widths) + 2 * (len(headers) - 1))}")
    for row in rows:
        print(f"  " + "  ".join(f"{c:<{w}}" for c, w in zip(row, col_widths)))

    # Aggregate
    total_tokens = sum(
        p.get_summary().get('total_tokens', 0) for p in parsers.values()
    )
    total_improvement = sum(
        p.get_summary().get('total_improvement', 0) for p in parsers.values()
    )
    total_versions = sum(
        p.get_summary().get('total_versions_created', 0) for p in parsers.values()
    )
    print(f"\n  AGGREGATE (all tasks):")
    print(f"    Total tokens consumed:  {total_tokens:,}")
    print(f"    Total bytes improved:   {total_improvement}")
    print(f"    Total versions created: {total_versions}")
    print(f"    Overall efficiency:     {total_improvement / max(total_tokens, 1):.6f} B/token")

    # Per-stage efficiency
    print(f"\n  STAGE EFFICIENCY BY TASK:")
    for task_name, parser in parsers.items():
        print(f"\n  --- {task_name} ---")
        stages = parser.get_stages()
        prev_end = 0
        for s in stages:
            tokens_here = s.end_tokens - prev_end
            prev_end = s.end_tokens
            eff = f"{s.improvement_bytes / max(tokens_here, 1):.4f} B/tok" if tokens_here > 0 else "N/A"
            print(f"    {s.name[:50]:<50s} | {tokens_here:>10,} tokens | "
                  f"improvement: {s.improvement_bytes:>4d}B | {eff}")


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

    # Color palette per task
    TASK_COLORS = {
        'task001': '#3b82f6', 'task002': '#ef4444', 'task003': '#10b981',
        'task004': '#f59e0b', 'task005': '#8b5cf6',
    }
    STAGE_COLORS = {
        '1. Understanding & First Solution': '#f59e0b',
        '2. Algorithm Exploration': '#3b82f6',
        '3. Micro-Optimization (Golfing)': '#8b5cf6',
    }

    # ─── Figure 1: Bytes vs Tokens (all tasks in one chart) ───
    fig, axes = plt.subplots(2, 2, figsize=(18, 13))
    fig.suptitle('Claude Experiment — Code Golf History Analysis (Tasks 001–005)',
                 fontsize=15, fontweight='bold')
    ax1, ax2, ax3, ax4 = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    for task_name, parser in parsers.items():
        traj = parser.get_best_bytes_curve()
        if not traj:
            continue

        color = TASK_COLORS.get(task_name, '#6b7280')
        tokens = [t['cumulative_tokens'] for t in traj]
        bytes_vals = [t['bytes'] for t in traj]
        turns = [t['conversation_turn'] for t in traj]

        # Plot 1: Bytes vs Tokens
        ax1.plot(tokens, bytes_vals, '-o', color=color, label=task_name,
                 linewidth=2, markersize=7, markerfacecolor=color,
                 markeredgewidth=1, alpha=0.85)
        ax1.fill_between(tokens, bytes_vals, alpha=0.05, color=color)
        # Annotate first and last
        ax1.annotate(f"{bytes_vals[0]}B", (tokens[0], bytes_vals[0]),
                     textcoords="offset points", xytext=(8, 0),
                     fontsize=7, color=color, alpha=0.7)
        ax1.annotate(f"{bytes_vals[-1]}B", (tokens[-1], bytes_vals[-1]),
                     textcoords="offset points", xytext=(8, -8),
                     fontsize=7, color=color, fontweight='bold')

        # Plot 2: Bytes vs Turns
        ax2.plot(turns, bytes_vals, '-s', color=color, label=task_name,
                 linewidth=2, markersize=7, markerfacecolor=color,
                 markeredgewidth=1, alpha=0.85)
        ax2.fill_between(turns, bytes_vals, alpha=0.05, color=color)

        # Plot 3: Token accumulation
        ax3.plot(turns, tokens, '-^', color=color, label=task_name,
                 linewidth=2, markersize=6, alpha=0.85)

        # Plot 4: Efficiency (bytes saved per token per improvement)
        efficiencies = []
        for i in range(1, len(traj)):
            dbytes = traj[i-1]['bytes'] - traj[i]['bytes']
            dtokens = traj[i]['cumulative_tokens'] - traj[i-1]['cumulative_tokens']
            if dtokens > 0 and dbytes > 0:
                efficiencies.append(dbytes / dtokens)
        if efficiencies:
            ax4.plot(range(1, len(efficiencies) + 1), efficiencies,
                     '-D', color=color, label=task_name,
                     linewidth=1.5, markersize=6, alpha=0.85)

    for ax, xlab, ylab, title in [
        (ax1, 'Cumulative Tokens', 'Best Code Length (bytes)',
         'Solution Size vs Tokens Consumed'),
        (ax2, 'Conversation Turns', 'Best Code Length (bytes)',
         'Solution Size vs Conversation Turns'),
    ]:
        ax.set_xlabel(xlab, fontsize=11)
        ax.set_ylabel(ylab, fontsize=11)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.legend(loc='upper right', framealpha=0.9, fontsize=8)
        ax.grid(True, alpha=0.2)
        ax.invert_yaxis()

    ax3.set_xlabel('Conversation Turns', fontsize=11)
    ax3.set_ylabel('Cumulative Tokens', fontsize=11)
    ax3.set_title('Token Consumption Over Turns', fontsize=13, fontweight='bold')
    ax3.legend(loc='lower right', framealpha=0.9, fontsize=8)
    ax3.grid(True, alpha=0.2)

    ax4.set_xlabel('Improvement Step #', fontsize=11)
    ax4.set_ylabel('Bytes Saved per Token', fontsize=11)
    ax4.set_title('Marginal Efficiency (Δbytes / Δtokens per improvement)',
                  fontsize=13, fontweight='bold')
    ax4.legend(loc='upper right', framealpha=0.9, fontsize=8)
    ax4.grid(True, alpha=0.2, axis='y')

    plt.tight_layout()
    p1 = out / 'claude_all_tasks_curves.png'
    plt.savefig(p1, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {p1}")

    # ─── Figure 2: Stage breakdown per task ───
    n_tasks = len(parsers)
    fig2, axes2 = plt.subplots(1, n_tasks, figsize=(5 * n_tasks, 5),
                                squeeze=False)
    fig2.suptitle('Problem-Solving Stages per Task', fontsize=14, fontweight='bold')

    for idx, (task_name, parser) in enumerate(parsers.items()):
        ax = axes2[0, idx]
        stages = parser.get_stages()
        if not stages:
            ax.set_title(f'{task_name} (no data)')
            continue

        names = [s.name.split('. ')[-1][:20] for s in stages]
        tokens_list = [s.end_tokens - s.start_tokens for s in stages]
        imp_list = [s.improvement_bytes for s in stages]
        colors = [STAGE_COLORS.get(s.name, '#6b7280') for s in stages]

        x = range(len(stages))
        bars = ax.bar(x, tokens_list, color=colors, alpha=0.85, edgecolor='white')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=30, ha='right', fontsize=7)
        ax.set_title(task_name, fontsize=11, fontweight='bold')
        ax.set_ylabel('Tokens', fontsize=9)
        ax.grid(True, alpha=0.2, axis='y')

        # Add improvement annotations on bars
        for bar, imp, name in zip(bars, imp_list, names):
            if imp > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + max(tokens_list) * 0.02,
                        f'-{imp}B', ha='center', fontsize=7,
                        fontweight='bold', color='#374151')
            # Token count inside bar if tall enough
            if bar.get_height() > max(tokens_list) * 0.15:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() / 2,
                        f'{int(bar.get_height()):,}',
                        ha='center', va='center', fontsize=6.5,
                        color='white', fontweight='bold', rotation=90)

    plt.tight_layout()
    p2 = out / 'claude_stage_breakdown.png'
    plt.savefig(p2, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {p2}")

    # ─── Figure 3: Summary bar chart ───
    fig3, (ax_s1, ax_s2) = plt.subplots(1, 2, figsize=(14, 5))
    fig3.suptitle('Claude Code Golf — Task Summary', fontsize=14, fontweight='bold')

    task_names = list(parsers.keys())
    x = np.arange(len(task_names))

    final_bytes = [parsers[t].get_summary().get('final_bytes', 0) for t in task_names]
    init_bytes = [parsers[t].get_summary().get('initial_bytes', 0) for t in task_names]
    total_toks = [parsers[t].get_summary().get('total_tokens', 0) for t in task_names]

    colors_list = [TASK_COLORS.get(t, '#6b7280') for t in task_names]

    # Improvement bar
    improvements = [init_bytes[i] - final_bytes[i] for i in range(len(task_names))]
    bars1 = ax_s1.bar(x, improvements, color=colors_list, alpha=0.85,
                      edgecolor='white', linewidth=1.5)
    ax_s1.set_xticks(x)
    ax_s1.set_xticklabels(task_names, fontsize=10)
    ax_s1.set_ylabel('Bytes Improved', fontsize=11)
    ax_s1.set_title('Total Byte Reduction per Task', fontsize=13, fontweight='bold')
    ax_s1.grid(True, alpha=0.2, axis='y')
    for bar, imp, init_b, final_b in zip(bars1, improvements, init_bytes, final_bytes):
        ax_s1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(improvements) * 0.02,
                   f'{init_b}B→{final_b}B\n(-{imp}B)',
                   ha='center', fontsize=8, fontweight='bold')

    # Token bar
    bars2 = ax_s2.bar(x, total_toks, color=colors_list, alpha=0.85,
                      edgecolor='white', linewidth=1.5)
    ax_s2.set_xticks(x)
    ax_s2.set_xticklabels(task_names, fontsize=10)
    ax_s2.set_ylabel('Total Tokens', fontsize=11)
    ax_s2.set_title('Token Consumption per Task', fontsize=13, fontweight='bold')
    ax_s2.grid(True, alpha=0.2, axis='y')
    for bar, tok in zip(bars2, total_toks):
        ax_s2.text(bar.get_x() + bar.get_width() / 2,
                   bar.get_height() + max(total_toks) * 0.02,
                   f'{tok:,}', ha='center', fontsize=8, fontweight='bold')

    plt.tight_layout()
    p3 = out / 'claude_summary.png'
    plt.savefig(p3, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: {p3}")


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

    json_path = out / 'claude_analysis.json'
    with open(json_path, 'w') as f:
        json.dump(export, f, indent=2, default=str)
    print(f"  Exported: {json_path}")


# ─── Main ──────────────────────────────────────────────────────────

def main():
    history_analysis_dir = Path(__file__).parent
    project_root = history_analysis_dir.parent
    output_dir = history_analysis_dir / 'output'

    # Discover all tasks in history-analysis
    tasks = {}
    for entry in sorted(history_analysis_dir.iterdir()):
        if not entry.is_dir() or not entry.name.startswith('-Users-'):
            continue
        # Extract task name: e.g. "deepseek-v4-pro-claude-task004" -> "task004"
        task_match = re.search(r'-(task\d{3})$', entry.name)
        if not task_match:
            continue
        task_name = task_match.group(1)

        # Find largest JSONL file (primary conversation)
        jsonl_files = sorted(entry.glob("*.jsonl"), key=lambda f: f.stat().st_size, reverse=True)
        if not jsonl_files:
            continue
        history_file = jsonl_files[0]

        workdir = project_root / 'deepseek-v4-pro-claude' / task_name / 'workdir'

        tasks[task_name] = {
            'history': history_file,
            'workdir': workdir,
        }

    if not tasks:
        print("No tasks found in history-analysis/")
        return

    print(f"Found {len(tasks)} tasks: {sorted(tasks.keys())}")
    print()

    parsers = {}
    for task_name in sorted(tasks.keys()):
        info = tasks[task_name]
        print(f"{'='*60}")
        print(f"  {task_name.upper()}")
        print(f"  History: {info['history']}")
        print(f"  Workdir: {info['workdir']}")
        print(f"{'='*60}")

        if not info['history'].exists():
            print(f"  SKIP: history not found")
            continue

        parser = HistoryParser(
            str(info['history']),
            str(info['workdir']),
        )
        parser.parse()
        parsers[task_name] = parser
        parser.print_report()

    # Cross-task summary
    if parsers:
        cross_task_summary(parsers)
        print(f"\n{'='*60}")
        print(f"  Generating plots & JSON export")
        print(f"{'='*60}")
        generate_plots(parsers, str(output_dir))
        export_json(parsers, str(output_dir))
        print(f"\n  ✓ Done! Check {output_dir}/")
    else:
        print("\n  No experiments parsed.")


if __name__ == '__main__':
    main()
