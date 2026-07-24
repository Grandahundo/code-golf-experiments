#!/usr/bin/env python3
"""
Default 实验分析 — task001 到 task005
- 有 history 的 task：完整轨迹分析（主 agent + subagents）
- 没有 history 的 task：仅展示 workdir 版本字节数
"""

import json
import os
import re
import sys
from pathlib import Path
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════
#  Parser (same logic as per_task_charts.py)
# ═══════════════════════════════════════════════════════════════

def parse_agent_history(history_path: str, workdir_path: str) -> dict:
    hp = Path(history_path)
    wd = Path(workdir_path)

    # ── measure disk files ──
    file_bytes = {}
    if wd.exists():
        for f in wd.glob("*.py"):
            try:
                file_bytes[f.name] = len(f.read_bytes())
            except Exception:
                pass

    # ── read JSONL ──
    events = []
    if hp.exists():
        with open(hp) as fh:
            for i, line in enumerate(fh):
                try:
                    events.append({'line': i, 'data': json.loads(line)})
                except json.JSONDecodeError:
                    continue

    # ── collect verified byte counts from text ──
    verified = set()
    for ev in events:
        d = ev['data']
        if d.get('type') != 'assistant':
            continue
        for c in d.get('message', {}).get('content', []):
            if isinstance(c, dict) and c.get('type') == 'text':
                text = c.get('text', '')
                for m in re.finditer(
                    r'(\d{2,4})\s*bytes?\s*(?:and|,)\s*pass(?:es|ing)?\s+all\s+tests',
                    text, re.IGNORECASE
                ):
                    bc = int(m.group(1))
                    if bc < 500: verified.add(bc)
                for m in re.finditer(
                    r'best\s*:\s*(\d{2,4})\s*b', text, re.IGNORECASE
                ):
                    bc = int(m.group(1))
                    if bc < 500: verified.add(bc)
                for m in re.finditer(
                    r'(?:verified|achieved|down to|now at|improved to|'
                    r'currently at|final|Length:\*\*\s*).*?(\d{2,4})',
                    text, re.IGNORECASE
                ):
                    bc = int(m.group(1))
                    if 20 <= bc < 500: verified.add(bc)

    # ── detect version write events ──
    write_events = []
    for ev in events:
        d = ev['data']
        if d.get('type') != 'assistant':
            continue
        for c in d.get('message', {}).get('content', []):
            if not isinstance(c, dict) or c.get('type') != 'tool_use':
                continue
            name = c.get('name', '')
            inp = c.get('input', {})
            if name == 'Write':
                fp = inp.get('file_path', '')
                fname = os.path.basename(fp)
                if re.match(r'.*\.py$', fname):
                    write_events.append({
                        'line': ev['line'], 'filename': fname,
                        'content': inp.get('content', ''),
                    })
            if name == 'Bash':
                cmd = inp.get('command', '')
                for m in re.finditer(
                    r'(?:cat|printf)\s.*?>\s*(?:.*?/)?(\S+\.py)\b', cmd
                ):
                    fname = m.group(1)
                    content_str = ''
                    hm = re.search(r"<<'EOF'\n(.*?)\nEOF", cmd, re.DOTALL)
                    if hm:
                        content_str = hm.group(1)
                    else:
                        pm = re.search(r"printf\s+'(.*)'\s*>", cmd)
                        if pm:
                            content_str = pm.group(1)
                    write_events.append({
                        'line': ev['line'], 'filename': fname,
                        'content': content_str,
                    })

    # ── accumulate tokens + record versions ──
    cumulative_tokens = 0
    turn_count = 0
    detailed_versions = []
    write_idx = 0
    seen = set()

    for ev in events:
        if ev['data'].get('type') == 'assistant':
            turn_count += 1
            usage = ev['data'].get('message', {}).get('usage', {})
            cumulative_tokens += usage.get('input_tokens', 0)
            cumulative_tokens += usage.get('output_tokens', 0)

        while (write_idx < len(write_events)
               and write_events[write_idx]['line'] <= ev['line']):
            we = write_events[write_idx]
            fname = we['filename']
            base_match = re.match(r'((?:agent[ABCQZ]?_)?v?\d+)', fname)
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
                    detailed_versions.append({
                        'version': vname,
                        'filename': fname,
                        'bytes': bc,
                        'line': we['line'],
                        'tokens': cumulative_tokens,
                        'turn': turn_count,
                        'verified': bc in verified,
                    })
            write_idx += 1

    # ── monotonic trajectory ──
    trajectory = []
    best = float('inf')
    for v in sorted(detailed_versions, key=lambda x: x['line']):
        bc = v['bytes']
        if bc < 20: continue
        if bc < best:
            best = bc
            trajectory.append({
                'version': v['version'],
                'filename': v.get('filename', ''),
                'bytes': bc,
                'tokens': v['tokens'],
                'turn': v['turn'],
                'verified': v['verified'],
            })

    if trajectory:
        first = trajectory[0]; last = trajectory[-1]
        total_imp = first['bytes'] - last['bytes']
    else:
        first = last = {'bytes': 0, 'version': '?'}
        total_imp = 0

    return {
        'agent_name': hp.stem[:8],
        'history_file': str(hp),
        'trajectory': trajectory,
        'all_versions': detailed_versions,
        'total_tokens': cumulative_tokens,
        'total_versions': len(detailed_versions),
        'turn_count': turn_count,
        'initial_bytes': first['bytes'],
        'final_bytes': last['bytes'],
        'improvement': total_imp,
        'improvement_pct': round(total_imp / first['bytes'] * 100, 1) if first['bytes'] > 0 else 0,
    }


# ═══════════════════════════════════════════════════════════════
#  Per-task chart
# ═══════════════════════════════════════════════════════════════

def plot_task(task_name: str, agents: list, workdir_versions: list, output_path: str):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    PALETTE = ['#2563eb', '#dc2626', '#16a34a', '#9333ea', '#ea580c',
               '#0891b2', '#d97706', '#4f46e5', '#be123c', '#0d9488']

    fig, ax = plt.subplots(figsize=(12, 6.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    has_history = len(agents) > 0

    if has_history:
        agents = sorted(agents, key=lambda a: a['total_tokens'], reverse=True)
        if len(agents) == 1:
            labels = ['main agent']
        else:
            labels = ['main agent'] + [f'ag#{i+1}' for i in range(1, len(agents))]

        total_tokens_all = 0
        best_tokens_all = 0

        for ag_idx, (agent, label) in enumerate(zip(agents, labels)):
            traj = agent['trajectory']
            if not traj: continue

            color = PALETTE[ag_idx % len(PALETTE)]
            total_tokens_all += agent['total_tokens']

            tokens_abs = [t['tokens'] for t in traj]
            bytes_vals = [t['bytes'] for t in traj]
            ver_flags = [t.get('verified', False) for t in traj]

            ls = '-' if ag_idx == 0 else '--'
            lw = 2.5 if ag_idx == 0 else 1.8
            ax.plot(tokens_abs, bytes_vals, ls, color=color,
                    linewidth=lw, alpha=0.85, zorder=2)

            for i in range(len(traj)):
                is_ver = ver_flags[i]
                ax.scatter(tokens_abs[i], bytes_vals[i],
                          c=color, s=100 if is_ver else 60,
                          zorder=4 if is_ver else 3,
                          edgecolors='white', linewidths=1.2 if is_ver else 0.6,
                          alpha=0.95, marker='D' if is_ver else 'o')

            # annotate first, last, verified, big jumps
            key_set = {0, len(traj) - 1}
            for i in range(1, len(traj)):
                if ver_flags[i]: key_set.add(i)
                dbytes = traj[i-1]['bytes'] - traj[i]['bytes']
                if dbytes > 10 or (traj[i-1]['bytes'] > 0 and dbytes / traj[i-1]['bytes'] > 0.1):
                    key_set.add(i)

            for i in sorted(key_set):
                t = traj[i]
                vlabel = f'{t["filename"] or t["version"]} ({t["bytes"]}B)'
                if len(agents) > 1:
                    vlabel = f'{label} {vlabel}'
                offsets = [(10, -12), (-10, -24), (12, -36), (-8, -10), (15, -10)]
                ox, oy = offsets[i % len(offsets)]
                fs = 7.5 if ver_flags[i] else 6.5
                ax.annotate(vlabel, (tokens_abs[i], bytes_vals[i]),
                           textcoords="offset points", xytext=(ox, oy),
                           fontsize=fs, color=color,
                           fontweight='bold' if ver_flags[i] else 'normal')

            traj_tok = traj[-1]['tokens'] if traj else 0

        # Legend
        legend_els = []
        for ag_idx, (agent, label) in enumerate(zip(agents, labels)):
            color = PALETTE[ag_idx % len(PALETTE)]
            ls = '-' if ag_idx == 0 else '--'
            traj_tok = agent['trajectory'][-1]['tokens'] if agent['trajectory'] else 0
            legend_els.append(
                Line2D([0], [0], color=color, linestyle=ls, linewidth=2,
                       marker='o', markersize=7, markerfacecolor=color,
                       label=f'{label}: {agent["initial_bytes"]}B→{agent["final_bytes"]}B '
                             f'({agent["improvement_pct"]}%), {traj_tok:,} tok to best')
            )
        ax.legend(handles=legend_els, loc='upper right',
                  framealpha=0.9, fontsize=7.5, edgecolor='#ddd')

        ax.set_xlabel('Tokens Consumed (per agent)', fontsize=11, color='#555')
        ax.set_title(f'Task {task_name[-3:]} (default) — {len(agents)} agent(s) with history',
                     fontsize=15, fontweight='bold', color='#222', pad=12)

        # summary
        all_initial = max(a['initial_bytes'] for a in agents if a['trajectory'])
        all_final = min(a['final_bytes'] for a in agents if a['trajectory'])
        all_imp = all_initial - all_final
        all_pct = round(all_imp / all_initial * 100, 1) if all_initial > 0 else 0
        best_tokens_all = sum(a['trajectory'][-1]['tokens'] for a in agents if a['trajectory'])
        total_vers = sum(a['total_versions'] for a in agents)

        summary_text = (
            f"Overall: {all_initial}B → {all_final}B ({all_pct}% reduction)"
            f"  |  Tokens to best: {best_tokens_all:,}"
            f"  |  Total session: {total_tokens_all:,}"
            f"  |  {total_vers} tracked versions"
        )
        ax.text(0.02, 0.02, summary_text, transform=ax.transAxes,
                fontsize=8.5, color='#888', fontstyle='italic', family='monospace',
                bbox=dict(boxstyle='round,pad=0.4', fc='#fafafa', ec='#eee', alpha=0.85))

    else:
        # No history — just show workdir versions as a bar chart
        if workdir_versions:
            names = [v['name'] for v in workdir_versions]
            bytes_list = [v['bytes'] for v in workdir_versions]
            colors = ['#2563eb' if v['bytes'] == min(bytes_list) else '#94a3b8'
                      for v in workdir_versions]

            bars = ax.bar(range(len(names)), bytes_list, color=colors,
                         alpha=0.85, edgecolor='white')
            ax.set_xticks(range(len(names)))
            ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)
            ax.set_ylabel('Code Length (bytes)', fontsize=11, color='#555')

            # annotate
            for bar, bc in zip(bars, bytes_list):
                ax.text(bar.get_x() + bar.get_width()/2, bc + max(bytes_list)*0.02,
                       f'{bc}B', ha='center', fontsize=8, fontweight='bold')

            best_idx = bytes_list.index(min(bytes_list))
            ax.set_title(f'Task {task_name[-3:]} (default) — workdir only (no history)',
                        fontsize=15, fontweight='bold', color='#222', pad=12)

            summary_text = (
                f"Best: {min(bytes_list)}B ({names[best_idx]})"
                f"  |  {len(workdir_versions)} files in workdir"
                f"  |  No conversation history available"
            )
        else:
            ax.text(0.5, 0.5, 'No data', transform=ax.transAxes,
                   ha='center', va='center', fontsize=14, color='#999')
            summary_text = 'No workdir files found'

        ax.text(0.02, 0.02, summary_text, transform=ax.transAxes,
                fontsize=8.5, color='#888', fontstyle='italic', family='monospace',
                bbox=dict(boxstyle='round,pad=0.4', fc='#fafafa', ec='#eee', alpha=0.85))

    ax.set_ylabel('Code Length (bytes)', fontsize=11, color='#555')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.15, linestyle='--', linewidth=0.5)
    ax.tick_params(labelsize=9, colors='#555')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#ccc')
    ax.spines['bottom'].set_color('#ccc')

    fig.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()


# ═══════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════

def main():
    project_root = Path(__file__).parent.parent
    default_dir = project_root / 'deepseek-v4-pro-default'
    history_analysis_dir = Path(__file__).parent  # <-- correct location
    output_dir = Path(__file__).parent / 'output' / 'default'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  DEFAULT EXPERIMENT ANALYSIS — task001 to task005")
    print("=" * 60)

    for task_name in sorted([f'task{t:03d}' for t in range(1, 6)]):
        workdir = default_dir / task_name / 'workdir'
        print(f'\n{"─"*50}')
        print(f'  {task_name.upper()}')
        print(f'  {"─"*50}')

        # Workdir versions
        workdir_versions = []
        if workdir.exists():
            for f in sorted(workdir.glob("*.py")):
                try:
                    bc = len(f.read_bytes())
                    workdir_versions.append({'name': f.name, 'bytes': bc})
                except Exception:
                    pass

        # Find history files in history-analysis/ (matching pattern: *default-taskXXX)
        agents = []
        for entry in history_analysis_dir.iterdir():
            if not entry.is_dir():
                continue
            if f'default-{task_name}' in entry.name:
                jsonl_files = sorted(entry.glob("*.jsonl"),
                                    key=lambda f: f.stat().st_size, reverse=True)
                # Main history (top-level jsonl)
                for jf in jsonl_files:
                    agent = parse_agent_history(str(jf), str(workdir))
                    if agent['trajectory'] or agent['all_versions']:
                        agents.append(agent)

                # Subagent histories in uuid/subagents/
                for item in entry.iterdir():
                    if item.is_dir():
                        sa_dir = item / 'subagents'
                        if sa_dir.exists():
                            for sa_file in sorted(sa_dir.glob("agent-*.jsonl")):
                                sa_agent = parse_agent_history(str(sa_file), str(workdir))
                                if sa_agent['trajectory'] or sa_agent['all_versions']:
                                    meta_file = sa_dir / f"{sa_file.stem}.meta.json"
                                    if meta_file.exists():
                                        try:
                                            meta = json.loads(meta_file.read_text())
                                            sa_agent['agent_name'] = meta.get('description', sa_file.stem[:8])
                                        except:
                                            pass
                                    agents.append(sa_agent)

        # Print summary
        if agents:
            for ag in agents:
                best_tok = ag['trajectory'][-1]['tokens'] if ag['trajectory'] else 0
                print(f'  [{ag["agent_name"]}] {ag["initial_bytes"]}B→{ag["final_bytes"]}B '
                      f'({ag["improvement_pct"]}%), {best_tok:,} tok to best / '
                      f'{ag["total_tokens"]:,} session, '
                      f'{len(ag["trajectory"])} improvements')

            all_final = min(a['final_bytes'] for a in agents if a['trajectory'])
            all_tok = sum(a['total_tokens'] for a in agents)
            best_tok_sum = sum(a['trajectory'][-1]['tokens'] for a in agents if a['trajectory'])
            print(f'  Best overall: {all_final}B | '
                  f'Tokens to best: {best_tok_sum:,} | Session total: {all_tok:,}')
        else:
            # No history, just show workdir
            if workdir_versions:
                print(f'  No conversation history found.')
                best = min(workdir_versions, key=lambda v: v['bytes'])
                print(f'  Workdir: {len(workdir_versions)} files, best = {best["name"]} ({best["bytes"]}B)')
                for v in workdir_versions:
                    marker = ' ← BEST' if v['bytes'] == best['bytes'] else ''
                    print(f'    {v["name"]}: {v["bytes"]}B{marker}')
            else:
                print(f'  No workdir files found.')

        # Plot
        output_path = str(output_dir / f'{task_name}_default.png')
        plot_task(task_name, agents, workdir_versions, output_path)
        print(f'  ✓ Chart: {output_path}')

    print(f'\n{"="*60}')
    print(f'  Charts saved in: {output_dir}/')


if __name__ == '__main__':
    main()
