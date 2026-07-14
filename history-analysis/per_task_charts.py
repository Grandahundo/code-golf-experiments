#!/usr/bin/env python3
"""
为每个 task 生成一张折线图。
- 每个 JSONL（agent）画一条线
- 主线 + 子 agent 各自独立轨迹
- 底部汇总所有 agent 的 token 总和
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

# ═══════════════════════════════════════════════════════════════
#  Lightweight per-agent parser (不依赖 analyze.py 的类)
# ═══════════════════════════════════════════════════════════════

def parse_agent_history(history_path: str, workdir_path: str) -> dict:
    """解析单个 JSONL，返回该 agent 的轨迹和统计"""

    hp = Path(history_path)
    wd = Path(workdir_path)

    # ── 测量磁盘上的实际文件 ──
    file_bytes = {}
    if wd.exists():
        for f in wd.glob("v*.py"):
            try:
                file_bytes[f.name] = len(f.read_bytes())
            except Exception:
                pass

    # ── 读 JSONL ──
    events = []
    if hp.exists():
        with open(hp) as fh:
            for i, line in enumerate(fh):
                try:
                    events.append({'line': i, 'data': json.loads(line)})
                except json.JSONDecodeError:
                    continue

    # ── 从对话文本收集 verified byte counts ──
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
                    if bc < 500:
                        verified.add(bc)
                for m in re.finditer(
                    r'best\s*:\s*(\d{2,4})\s*b',
                    text, re.IGNORECASE
                ):
                    bc = int(m.group(1))
                    if bc < 500:
                        verified.add(bc)
                for m in re.finditer(
                    r'(?:verified|achieved|down to|now at|improved to|'
                    r'currently at|final).*?(\d{2,4})\s*b',
                    text, re.IGNORECASE
                ):
                    bc = int(m.group(1))
                    if 20 <= bc < 500:
                        verified.add(bc)

    # ── 检测版本写入事件 ──
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

            # Write 工具
            if name == 'Write':
                fp = inp.get('file_path', '')
                fname = os.path.basename(fp)
                if re.match(r'v\d+.*\.py', fname):
                    write_events.append({
                        'line': ev['line'],
                        'filename': fname,
                        'content': inp.get('content', ''),
                    })

            # Bash 重定向
            if name == 'Bash':
                cmd = inp.get('command', '')
                for m in re.finditer(
                    r'(?:cat|printf)\s.*?>\s*(?:.*?/)?(v\d+.*?\.py)\b',
                    cmd
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
                        'line': ev['line'],
                        'filename': fname,
                        'content': content_str,
                    })

    # ── 累加 token + 记录版本 ──
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

        # 处理该行及之前的所有 write 事件
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
                    detailed_versions.append({
                        'version': vname,
                        'bytes': bc,
                        'line': we['line'],
                        'tokens': cumulative_tokens,
                        'turn': turn_count,
                        'verified': bc in verified,
                    })
            write_idx += 1

    # ── 构建单调递减轨迹 ──
    trajectory = []
    best = float('inf')
    for v in sorted(detailed_versions, key=lambda x: x['line']):
        bc = v['bytes']
        if bc < 20:
            continue
        if bc < best:
            best = bc
            trajectory.append({
                'version': v['version'],
                'bytes': bc,
                'tokens': v['tokens'],
                'turn': v['turn'],
                'verified': v['verified'],
            })

    # ── 汇总 ──
    if trajectory:
        first = trajectory[0]
        last = trajectory[-1]
        total_imp = first['bytes'] - last['bytes']
    else:
        first = last = {'bytes': 0, 'version': '?'}
        total_imp = 0

    return {
        'agent_name': hp.stem[:8],
        'history_file': str(hp),
        'trajectory': trajectory,
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

def plot_task(task_name: str, agents: List[dict], output_path: str):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    # ── color palette for agents ──
    PALETTE = ['#2563eb', '#dc2626', '#16a34a', '#9333ea', '#ea580c']

    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    all_points = []  # (tokens_offset, bytes, label, color, verified)

    # ── 按 token 总量排序（最多的当 main，放最前面） ──
    agents = sorted(agents, key=lambda a: a['total_tokens'], reverse=True)

    # ── 确定 label ──
    if len(agents) == 1:
        labels = ['main agent']
    else:
        labels = ['main agent'] + [f'agent #{i+1}' for i in range(1, len(agents))]

    total_tokens_all = 0

    for ag_idx, (agent, label) in enumerate(zip(agents, labels)):
        traj = agent['trajectory']
        if not traj:
            continue

        color = PALETTE[ag_idx % len(PALETTE)]
        total_tokens_all += agent['total_tokens']

        tokens_abs = [t['tokens'] for t in traj]
        bytes_vals = [t['bytes'] for t in traj]
        versions = [t['version'] for t in traj]
        ver_flags = [t.get('verified', False) for t in traj]

        # ── 画线 ──
        linestyle = '-' if ag_idx == 0 else '--'
        linewidth = 2.5 if ag_idx == 0 else 1.8
        ax.plot(tokens_abs, bytes_vals, linestyle, color=color,
                linewidth=linewidth, alpha=0.85, zorder=2)

        # ── 画点 ──
        for i in range(len(traj)):
            is_ver = ver_flags[i]
            ax.scatter(
                tokens_abs[i], bytes_vals[i],
                c=color, s=100 if is_ver else 60,
                zorder=4 if is_ver else 3,
                edgecolors='white', linewidths=1.2 if is_ver else 0.6,
                alpha=0.95, marker='D' if is_ver else 'o',
            )

        # ── 标注关键点 ──
        key_set = {0, len(traj) - 1}
        for i in range(1, len(traj)):
            if ver_flags[i]:
                key_set.add(i)
            dbytes = traj[i-1]['bytes'] - traj[i]['bytes']
            pct = dbytes / traj[i-1]['bytes'] * 100
            if pct > 10 or dbytes > 20:
                key_set.add(i)

        for i in sorted(key_set):
            t = traj[i]
            vlabel = f'{label}  {t["version"]} ({t["bytes"]}B)'
            offsets = [(10, -12), (-10, -24), (12, -36), (-8, -10)]
            ox, oy = offsets[i % len(offsets)]
            ax.annotate(
                vlabel,
                (tokens_abs[i], bytes_vals[i]),
                textcoords="offset points", xytext=(ox, oy),
                fontsize=7.5 if ver_flags[i] else 7,
                color=color, fontweight='bold' if ver_flags[i] else 'normal',
            )

    # ── 轴线 ──
    ax.set_xlabel('Tokens Consumed (per agent)', fontsize=11, color='#555')
    ax.set_ylabel('Best Code Length (bytes)', fontsize=11, color='#555')
    ax.set_title(f'Task {task_name[-3:]} — {len(agents)} agent(s)',
                 fontsize=15, fontweight='bold', color='#222', pad=12)
    ax.invert_yaxis()
    ax.grid(True, alpha=0.15, linestyle='--', linewidth=0.5)
    ax.tick_params(labelsize=9, colors='#555')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#ccc')
    ax.spines['bottom'].set_color('#ccc')

    # ── 图例 ──
    legend_els = []
    for ag_idx, (agent, label) in enumerate(zip(agents, labels)):
        color = PALETTE[ag_idx % len(PALETTE)]
        ls = '-' if ag_idx == 0 else '--'

        # trajectory-level tokens (consumed up to last improvement)
        traj_tok = agent['trajectory'][-1]['tokens'] if agent['trajectory'] else 0
        legend_els.append(
            Line2D([0], [0], color=color, linestyle=ls, linewidth=2,
                   marker='o', markersize=7, markerfacecolor=color,
                   label=f'{label}  ({agent["initial_bytes"]}B→{agent["final_bytes"]}B, '
                         f'{traj_tok:,} tok to best)')
        )
    ax.legend(handles=legend_els, loc='upper right',
              framealpha=0.9, fontsize=8, edgecolor='#ddd')

    # ── 底部汇总 ──
    # 找出全局最优
    all_initial = max(a['initial_bytes'] for a in agents if a['trajectory'])
    all_final = min(a['final_bytes'] for a in agents if a['trajectory'])
    all_imp = all_initial - all_final
    all_pct = round(all_imp / all_initial * 100, 1) if all_initial > 0 else 0
    total_vers = sum(a['total_versions'] for a in agents)

    # tokens consumed to reach best (sum of each agent's trajectory-end tokens)
    best_tokens = sum(
        a['trajectory'][-1]['tokens'] for a in agents if a['trajectory']
    )
    summary_text = (
        f"Overall: {all_initial}B → {all_final}B ({all_pct}% reduction)"
        f"  |  Tokens to best: {best_tokens:,}"
        f"  |  Total session: {total_tokens_all:,}"
        f"  |  {total_vers} versions across {len(agents)} agent(s)"
    )
    ax.text(
        0.02, 0.02, summary_text,
        transform=ax.transAxes, fontsize=8.5, color='#888',
        fontstyle='italic', family='monospace',
        bbox=dict(boxstyle='round,pad=0.4', fc='#fafafa', ec='#eee', alpha=0.85)
    )

    fig.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()

    # 打印摘要
    print(f'\n  {"─"*50}')
    print(f'  {task_name.upper()}  —  {len(agents)} agent(s)')
    print(f'  {"─"*50}')
    for ag_idx, (agent, label) in enumerate(zip(agents, labels)):
        best_tok = agent['trajectory'][-1]['tokens'] if agent['trajectory'] else 0
        print(f'  {label}: {agent["initial_bytes"]}B→{agent["final_bytes"]}B '
              f'({agent["improvement_pct"]}%), '
              f'{best_tok:,} tok to best / {agent["total_tokens"]:,} session total, '
              f'{agent["total_versions"]} versions, '
              f'{len(agent["trajectory"])} improvements')
    best_tokens = sum(
        a['trajectory'][-1]['tokens'] for a in agents if a['trajectory']
    )
    print(f'  {"─"*50}')
    print(f'  COMBINED: {all_initial}B→{all_final}B ({all_pct}%), '
          f'{best_tokens:,} tok to best / {total_tokens_all:,} session total')
    best_tokens = sum(
        a['trajectory'][-1]['tokens'] for a in agents if a['trajectory']
    )
    return best_tokens, total_tokens_all


# ═══════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════

def main():
    history_analysis_dir = Path(__file__).parent
    project_root = history_analysis_dir.parent
    output_dir = history_analysis_dir / 'output' / 'per_task'
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── 发现所有 task ──
    tasks = {}
    for entry in sorted(history_analysis_dir.iterdir()):
        if not entry.is_dir() or not entry.name.startswith('-Users-'):
            continue
        m = re.search(r'-(task\d{3})$', entry.name)
        if not m:
            continue
        task_name = m.group(1)
        workdir = project_root / 'deepseek-v4-pro-claude' / task_name / 'workdir'
        jsonl_files = sorted(entry.glob("*.jsonl"),
                            key=lambda f: f.stat().st_size, reverse=True)
        tasks[task_name] = {'jsonl_files': jsonl_files, 'workdir': workdir}

    grand_best = 0
    grand_session = 0

    for task_name in sorted(tasks.keys()):
        info = tasks[task_name]
        agents = []
        for jf in info['jsonl_files']:
            agent = parse_agent_history(str(jf), str(info['workdir']))
            agents.append(agent)

        output_path = str(output_dir / f'{task_name}_trajectory.png')
        tokens_best, tokens_session = plot_task(task_name, agents, output_path)
        grand_best += tokens_best
        grand_session += tokens_session
        print(f'  ✓ Chart saved: {output_path}')

    print(f'\n{"="*60}')
    print(f'  GRAND TOTAL across all tasks:')
    print(f'    Tokens to best:   {grand_best:,}')
    print(f'    Total session:    {grand_session:,}')
    print(f'  Charts saved in: {output_dir}/')


if __name__ == '__main__':
    main()
