#!/usr/bin/env python3
"""
Claude vs Default 对比折线图 —— 每个 task 一张
- 以 workdir .py 文件字节数为 ground truth
- 主线 + subagent 各自独立画线
- 两套实验同图对比
"""

import json, os, re, sys
from pathlib import Path
from collections import defaultdict


# ═══════════════════════════════════════════════════════════
#  Parser — 以 workdir 文件大小为 ground truth
# ═══════════════════════════════════════════════════════════

def parse_agent(history_path: str, workdir_path: str, agent_label: str = "") -> dict:
    """解析单个 JSONL，只记录 workdir 中实际存在的版本"""
    hp = Path(history_path)
    wd = Path(workdir_path)

    # ── ground truth: workdir 里的实际文件（排除 numpy 等外部依赖） ──
    file_bytes = {}
    if wd.exists():
        for f in wd.glob("*.py"):
            try:
                content = f.read_bytes()
                text = content.decode('utf-8', errors='replace')
                # 排除用了外部库的文件 (numpy, scipy, etc.)
                if re.search(r'(?:import numpy|from numpy|import scipy|from scipy)', text):
                    continue
                file_bytes[f.name] = len(content)
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

    # ── 检测写入事件（只关心匹配 workdir 中实际文件的写入） ──
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
                if fname in file_bytes:  # 必须在 workdir 中存在
                    write_events.append({'line': ev['line'], 'filename': fname})

            if name == 'Bash':
                cmd = inp.get('command', '')
                for m in re.finditer(r'(?:cat|printf)\s.*?>\s*(?:.*?/)?(\S+\.py)\b', cmd):
                    fname = m.group(1)
                    if fname in file_bytes:
                        write_events.append({'line': ev['line'], 'filename': fname})

    # ── 累加 token + 记录版本 ──
    cumulative_tokens = 0
    turn_count = 0
    detailed_versions = []
    write_idx = 0
    seen_files = set()

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
            if fname not in seen_files:
                seen_files.add(fname)
                bc = file_bytes.get(fname, 0)
                if bc >= 20:  # 过滤无效文件
                    detailed_versions.append({
                        'filename': fname,
                        'bytes': bc,
                        'line': we['line'],
                        'tokens': cumulative_tokens,
                        'turn': turn_count,
                    })
            write_idx += 1

    # ── 按行号排序，构建单调递减轨迹 ──
    trajectory = []
    versions_by_time = sorted(detailed_versions, key=lambda x: x['line'])
    best = float('inf')
    for v in versions_by_time:
        bc = v['bytes']
        if bc < best:
            best = bc
            trajectory.append({
                'filename': v['filename'],
                'bytes': bc,
                'tokens': v['tokens'],
                'turn': v['turn'],
            })

    if trajectory:
        first, last = trajectory[0], trajectory[-1]
        imp = first['bytes'] - last['bytes']
        pct = round(imp / first['bytes'] * 100, 1) if first['bytes'] > 0 else 0
    else:
        first = last = {'bytes': 0, 'filename': '?'}
        imp = pct = 0

    return {
        'label': agent_label,
        'history_file': str(hp),
        'trajectory': trajectory,
        'total_tokens': cumulative_tokens,
        'total_files': len(detailed_versions),
        'initial_bytes': first['bytes'],
        'final_bytes': last['bytes'],
        'improvement': imp,
        'improvement_pct': pct,
    }


# ═══════════════════════════════════════════════════════════
#  对比折线图
# ═══════════════════════════════════════════════════════════

def plot_comparison(task_name: str, claude_agents: list, default_agents: list,
                    output_path: str):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    fig, ax = plt.subplots(figsize=(13, 6.5))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # ── 颜色体系 ──
    CLAUDE_MAIN = '#2563eb'      # blue solid
    CLAUDE_SUB = '#60a5fa'       # blue dashed
    DEFAULT_MAIN = '#dc2626'     # red solid
    DEFAULT_SUB = '#f87171'      # red dashed

    all_lines = []  # for legend

    # ── Claude: 只画主线（最大的那个 agent） ──
    claude_main = max(claude_agents, key=lambda a: a['total_tokens'], default=None)
    claude_others = sorted(
        [a for a in claude_agents if a is not claude_main and len(a['trajectory']) >= 2],
        key=lambda a: a['total_tokens'], reverse=True)
    claude_to_plot = ([claude_main] if claude_main else []) + claude_others
    for ag_idx, agent in enumerate(claude_to_plot):
        traj = agent['trajectory']
        if not traj or len(traj) < 1:
            continue

        is_main = (ag_idx == 0)
        color = CLAUDE_MAIN if is_main else CLAUDE_SUB
        ls = '-' if is_main else '--'
        lw = 2.5 if is_main else 1.5
        alpha = 0.9 if is_main else 0.55

        tokens_abs = [t['tokens'] for t in traj]
        bytes_vals = [t['bytes'] for t in traj]

        ax.plot(tokens_abs, bytes_vals, ls, color=color, linewidth=lw,
                alpha=alpha, zorder=3 if is_main else 1)
        ax.scatter(tokens_abs, bytes_vals, c=color, s=70 if is_main else 35,
                  zorder=4 if is_main else 2, edgecolors='white',
                  linewidths=1 if is_main else 0.5, alpha=alpha)

        # 只标注首尾
        for i in (0, len(traj) - 1):
            if i == len(traj) - 1 and is_main:
                # 最终最优加粗
                ax.annotate(f'{traj[i]["bytes"]}B',
                           (tokens_abs[i], bytes_vals[i]),
                           textcoords="offset points", xytext=(8, -14),
                           fontsize=10, color=color, fontweight='bold')
            elif i == 0 and is_main:
                ax.annotate(f'{traj[i]["bytes"]}B',
                           (tokens_abs[i], bytes_vals[i]),
                           textcoords="offset points", xytext=(8, 6),
                           fontsize=8, color=color, alpha=0.7)

        if is_main:
            all_lines.append((color, ls, lw, 'Claude',
                             agent['initial_bytes'], agent['final_bytes'],
                             traj[-1]['tokens']))

    # ── Default: 只画主线（最大的那个 agent） ──
    default_main = max(default_agents, key=lambda a: a['total_tokens'], default=None)
    default_others = sorted(
        [a for a in default_agents if a is not default_main and len(a['trajectory']) >= 2],
        key=lambda a: a['total_tokens'], reverse=True)
    default_to_plot = ([default_main] if default_main else []) + default_others
    for ag_idx, agent in enumerate(default_to_plot):
        traj = agent['trajectory']
        if not traj or len(traj) < 1:
            continue

        is_main = (ag_idx == 0)
        color = DEFAULT_MAIN if is_main else DEFAULT_SUB
        ls = '-' if is_main else '--'
        lw = 2.5 if is_main else 1.5
        alpha = 0.9 if is_main else 0.55

        tokens_abs = [t['tokens'] for t in traj]
        bytes_vals = [t['bytes'] for t in traj]

        ax.plot(tokens_abs, bytes_vals, ls, color=color, linewidth=lw,
                alpha=alpha, zorder=3 if is_main else 1)
        ax.scatter(tokens_abs, bytes_vals, c=color, s=70 if is_main else 35,
                  zorder=4 if is_main else 2, edgecolors='white',
                  linewidths=1 if is_main else 0.5, alpha=alpha)

        for i in (0, len(traj) - 1):
            if i == len(traj) - 1 and is_main:
                ax.annotate(f'{traj[i]["bytes"]}B',
                           (tokens_abs[i], bytes_vals[i]),
                           textcoords="offset points", xytext=(8, -14),
                           fontsize=10, color=color, fontweight='bold')
            elif i == 0 and is_main:
                ax.annotate(f'{traj[i]["bytes"]}B',
                           (tokens_abs[i], bytes_vals[i]),
                           textcoords="offset points", xytext=(8, 6),
                           fontsize=8, color=color, alpha=0.7)

        if is_main:
            all_lines.append((color, ls, lw, 'Default',
                             agent['initial_bytes'], agent['final_bytes'],
                             traj[-1]['tokens']))

    # ── 轴线 ──
    ax.set_xlabel('Tokens Consumed', fontsize=11, color='#555')
    ax.set_ylabel('Code Length (bytes)', fontsize=11, color='#555')
    ax.set_title(f'Task {task_name[-3:]} — Claude vs Default',
                 fontsize=15, fontweight='bold', color='#222', pad=12)
    ax.invert_yaxis()
    ax.grid(True, alpha=0.12, linestyle='--', linewidth=0.5)
    ax.tick_params(labelsize=9, colors='#555')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#ccc')
    ax.spines['bottom'].set_color('#ccc')

    # ── 图例 ──
    legend_els = []
    for color, ls, lw, label, init_b, final_b, tok in all_lines:
        legend_els.append(
            Line2D([0], [0], color=color, linestyle=ls, linewidth=2.5,
                   marker='o', markersize=8, markerfacecolor=color,
                   label=f'{label}: {init_b}B→{final_b}B ({tok:,} tok)')
        )
    ax.legend(handles=legend_els, loc='upper right',
              framealpha=0.92, fontsize=8.5, edgecolor='#ddd')

    # ── 底部汇总 ──
    # 从 workdir 取各自最优
    claude_best = min((a['final_bytes'] for a in claude_agents if a['trajectory']), default=None)
    default_best = min((a['final_bytes'] for a in default_agents if a['trajectory']), default=None)
    claude_tok = sum(a['trajectory'][-1]['tokens'] for a in claude_agents if a['trajectory'])
    default_tok = sum(a['trajectory'][-1]['tokens'] for a in default_agents if a['trajectory'])

    if claude_best and default_best:
        if claude_best < default_best:
            winner = f'Claude wins by {default_best - claude_best}B'
        elif default_best < claude_best:
            winner = f'Default wins by {claude_best - default_best}B'
        else:
            winner = 'Tie'
    else:
        winner = 'N/A'

    summary = (
        f"Claude best: {claude_best}B ({claude_tok:,} tok)  |  "
        f"Default best: {default_best}B ({default_tok:,} tok)  |  "
        f"{winner}"
    )
    ax.text(0.02, 0.02, summary, transform=ax.transAxes,
            fontsize=9, color='#555', fontstyle='italic', family='monospace',
            bbox=dict(boxstyle='round,pad=0.4', fc='#fafafa', ec='#eee', alpha=0.85))

    fig.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close()


# ═══════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════

def main():
    base = Path(__file__).parent
    project_root = base.parent
    output_dir = base / 'output' / 'compare'
    output_dir.mkdir(parents=True, exist_ok=True)

    tasks = ['task001', 'task002', 'task003', 'task004', 'task005']

    print("=" * 60)
    print("  CLAUDE vs DEFAULT — Per-Task Comparison")
    print("=" * 60)

    for task_name in tasks:
        claude_agents = []
        default_agents = []

        # ── Claude: history-analysis/*-claude-taskXXX/ ──
        for entry in base.iterdir():
            if not entry.is_dir(): continue
            if f'claude-{task_name}' not in entry.name: continue

            wd = project_root / 'deepseek-v4-pro-claude' / task_name / 'workdir'

            # main + subagents
            for jf in sorted(entry.glob("*.jsonl"), key=lambda f: f.stat().st_size, reverse=True):
                ag = parse_agent(str(jf), str(wd), "claude-main")
                if ag['trajectory']:
                    claude_agents.append(ag)

            for item in entry.iterdir():
                if item.is_dir():
                    sa_dir = item / 'subagents'
                    if sa_dir.exists():
                        for sa_file in sorted(sa_dir.glob("agent-*.jsonl")):
                            meta_file = sa_dir / f"{sa_file.stem}.meta.json"
                            desc = sa_file.stem[:8]
                            if meta_file.exists():
                                try:
                                    meta = json.loads(meta_file.read_text())
                                    desc = meta.get('description', desc)
                                except: pass
                            ag = parse_agent(str(sa_file), str(wd), desc[:50])
                            if ag['trajectory']:
                                claude_agents.append(ag)

        # ── Default: history-analysis/*-default-taskXXX/ ──
        for entry in base.iterdir():
            if not entry.is_dir(): continue
            if f'default-{task_name}' not in entry.name: continue

            wd = project_root / 'deepseek-v4-pro-default' / task_name / 'workdir'

            for jf in sorted(entry.glob("*.jsonl"), key=lambda f: f.stat().st_size, reverse=True):
                ag = parse_agent(str(jf), str(wd), "default-main")
                if ag['trajectory']:
                    default_agents.append(ag)

            for item in entry.iterdir():
                if item.is_dir():
                    sa_dir = item / 'subagents'
                    if sa_dir.exists():
                        for sa_file in sorted(sa_dir.glob("agent-*.jsonl")):
                            meta_file = sa_dir / f"{sa_file.stem}.meta.json"
                            desc = sa_file.stem[:8]
                            if meta_file.exists():
                                try:
                                    meta = json.loads(meta_file.read_text())
                                    desc = meta.get('description', desc)
                                except: pass
                            ag = parse_agent(str(sa_file), str(wd), desc[:50])
                            if ag['trajectory']:
                                default_agents.append(ag)

        # ── 打印 ──
        print(f'\n{"─"*50}')
        print(f'  {task_name.upper()}')
        print(f'  {"─"*50}')
        print(f'  Claude: {len(claude_agents)} agents')
        for a in claude_agents:
            print(f'    {a["initial_bytes"]}B→{a["final_bytes"]}B '
                  f'({a["improvement_pct"]}%), {len(a["trajectory"])} improvements, '
                  f'{a["trajectory"][-1]["tokens"]:,} tok')
        print(f'  Default: {len(default_agents)} agents')
        for a in default_agents:
            print(f'    {a["initial_bytes"]}B→{a["final_bytes"]}B '
                  f'({a["improvement_pct"]}%), {len(a["trajectory"])} improvements, '
                  f'{a["trajectory"][-1]["tokens"]:,} tok')

        c_best = min((a['final_bytes'] for a in claude_agents if a['trajectory']), default=None)
        d_best = min((a['final_bytes'] for a in default_agents if a['trajectory']), default=None)
        if c_best and d_best:
            if c_best < d_best: w = f'Claude wins ({c_best}B vs {d_best}B)'
            elif d_best < c_best: w = f'Default wins ({d_best}B vs {c_best}B)'
            else: w = f'Tie at {c_best}B'
            print(f'  → {w}')

        # ── 画图 ──
        output_path = str(output_dir / f'{task_name}_compare.png')
        plot_comparison(task_name, claude_agents, default_agents, output_path)
        print(f'  ✓ {output_path}')

    print(f'\n{"="*60}')
    print(f'  Done. Charts in {output_dir}/')


if __name__ == '__main__':
    main()
