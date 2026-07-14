#!/usr/bin/env python3
"""
Comprehensive History Visualizer — All 6 Experiments
=====================================================
Parses all experiment conversation histories and produces a rich
multi-panel dashboard comparing all approaches.

Output goes to: history/output/viz-YYYYMMDD-HHMMSS/
(Original data untouched — history dir is read-only from this script's POV.)

Experiments:
  1. Baseline        — deepseek-v4-pro standard code-golf
  2. CoMAP           — Cognitive Map agent scaffolding
  3. PAL             — Program-Aided Language reasoning
  4. PAL-lambda      — PAL with lambda-calculus style
  5. PAL-prompt-aug  — PAL with augmented prompts
  6. Claude           — Claude (Anthropic) baseline
"""

import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Repoint path so we can import HistoryParser from history_parser.py
HISTORY_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = HISTORY_DIR.parent

sys.path.insert(0, str(HISTORY_DIR))
from history_parser import HistoryParser, Stage

# ─── Experiment registry ──────────────────────────────────────────

EXPERIMENTS = [
    {
        'name': 'Baseline',
        'short': 'baseline',
        'history': (
            HISTORY_DIR
            / '-Users-jackson-Desktop-code-golf-deepseek-v4-pro-baseline-task004'
            / '841b42b7-cc0b-4b8d-b7c9-401d30acbf88.jsonl'
        ),
        'workdir': PROJECT_ROOT / 'deepseek-v4-pro-baseline' / 'task004' / 'workdir',
        'color': '#3b82f6',
        'marker': 'o',
    },
    {
        'name': 'CoMAP',
        'short': 'comap',
        'history': (
            HISTORY_DIR
            / '-Users-jackson-Desktop-code-golf-deepseek-v4-pro-CoMAP-task004'
            / '3e121c35-394b-4eb6-b472-20cc5495ee60.jsonl'
        ),
        'workdir': PROJECT_ROOT / 'deepseek-v4-pro-CoMAP' / 'task004' / 'workdir',
        'color': '#ef4444',
        'marker': 's',
    },
    {
        'name': 'PAL',
        'short': 'pal',
        'history': (
            HISTORY_DIR
            / '-Users-jackson-Desktop-code-golf-deepseek-v4-pro-PAL-task004'
            / '30d63a00-f253-4e09-8406-3600e7e043e7.jsonl'
        ),
        'workdir': PROJECT_ROOT / 'deepseek-v4-pro-PAL' / 'task004' / 'workdir',
        'color': '#10b981',
        'marker': 'D',
    },
    {
        'name': 'PAL-λ',
        'short': 'pal-lambda',
        'history': (
            HISTORY_DIR
            / '-Users-jackson-Desktop-code-golf-deepseek-v4-pro-PAL-lambda'
            / 'f6cffd37-4602-4811-ac37-183764ea6130.jsonl'
        ),
        'workdir': PROJECT_ROOT / 'deepseek-v4-pro-PAL-lambda' / 'task004' / 'workdir',
        'color': '#f59e0b',
        'marker': '^',
    },
    {
        'name': 'PAL-Aug',
        'short': 'pal-aug',
        'history': (
            HISTORY_DIR
            / '-Users-jackson-Desktop-code-golf-deepseek-v4-pro-PAL-prompt-augmented-task004'
            / 'f262efae-d353-473b-945f-10d1547c3bb5.jsonl'
        ),
        'workdir': PROJECT_ROOT / 'deepseek-v4-pro-PAL-prompt-augmented' / 'task004',
        'color': '#8b5cf6',
        'marker': 'v',
    },
    {
        'name': 'auto-PAL',
        'short': 'auto-pal',
        'history': (
            HISTORY_DIR
            / '-Users-jackson-Desktop-code-golf-deepseek-v4-pro-claude-task004'
            / '23276732-78d9-4ca4-bcd9-97231171a5ac.jsonl'
        ),
        'workdir': PROJECT_ROOT / 'deepseek-v4-pro-claude' / 'task004' / 'workdir',
        'color': '#ec4899',
        'marker': 'P',
    },
    {
        'name': 'Default',
        'short': 'default',
        'history': (
            HISTORY_DIR
            / '-Users-jackson-Desktop-code-golf-deepseek-v4-pro-default-task004'
            / '24f9062e-6dd3-43d6-ab9f-39a5b5238ba5.jsonl'
        ),
        'workdir': PROJECT_ROOT / 'deepseek-v4-pro-default' / 'task004' / 'workdir',
        'color': '#14b8a6',
        'marker': 'h',
    },
    {
        'name': 'Default-Aug',
        'short': 'default-aug',
        'history': (
            HISTORY_DIR
            / '-Users-jackson-Desktop-code-golf-deepseek-v4-pro-default-augmented-task004'
            / '35425b97-c27a-4abb-84d9-d866d643b5be.jsonl'
        ),
        'workdir': PROJECT_ROOT / 'deepseek-v4-pro-default-augmented' / 'task004' / 'workdir',
        'color': '#f97316',
        'marker': 'p',
    },
]

# ─── Colours & style constants ────────────────────────────────────

STAGE_COLORS = {
    '1. Understanding & First Solution': '#f59e0b',
    '2. Algorithm Exploration': '#3b82f6',
    '3. Micro-Optimization (Golfing)': '#8b5cf6',
    '4. Plateau / Converged': '#ef4444',
}

# ─── Main orchestration ───────────────────────────────────────────

def main():
    # 1. Parse all experiments
    parsers: Dict[str, HistoryParser] = {}

    for exp in EXPERIMENTS:
        name = exp['name']
        hist_path = exp['history']
        wd_path = exp['workdir']

        print(f"\n{'='*60}")
        print(f"  {name}")
        print(f"{'='*60}")

        if not hist_path.exists():
            print(f"  SKIP: history not found → {hist_path}")
            continue

        parser = HistoryParser(str(hist_path), str(wd_path))
        parser.parse()
        parsers[name] = parser
        parser.print_report()

        # Fallback: if parser found nothing (e.g. Claude uses Bash not Write),
        # build trajectory from workdir files + JSONL timeline
        if not parser.get_best_bytes_curve() and wd_path.exists():
            print(f"  → Trying fallback parser (workdir-based)...")
            fallback = parse_fallback(str(hist_path), str(wd_path))
            if fallback.get_best_bytes_curve():
                parsers[name] = fallback
                fallback.print_report()

    if not parsers:
        print("\n  [FAIL] No experiments parsed. Exiting.")
        return

    # 1.5 Subagent version discovery
    print(f"\n{'='*60}")
    print(f"  Subagent Version Discovery")
    print(f"{'='*60}")
    for name, parser in parsers.items():
        exp_info = next(e for e in EXPERIMENTS if e['name'] == name)
        subagent_traj = discover_subagent_versions(parser, str(exp_info['history']))
        if subagent_traj:
            print(f"  {name}: found {len(subagent_traj)} subagent versions, best={min(v['bytes'] for v in subagent_traj)}B")
            # Only merge for Default experiment (uses subagents extensively)
            if name == 'Default':
                _merge_subagent_trajectory(parser, subagent_traj)

    # 1.6 Correctness audit on all trajectories
    print(f"\n{'='*60}")
    print(f"  Correctness Audit")
    print(f"{'='*60}")
    for name, parser in parsers.items():
        exp_info = next(e for e in EXPERIMENTS if e['name'] == name)
        audit = run_correctness_audit(parser, str(exp_info['history']), exp_name=name)
        parser._audit = audit
        print_correctness_report(name, audit)

    # 2. Generate output
    ts = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_dir = HISTORY_DIR / 'output' / f'viz-{ts}'
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  Generating visualizations → {output_dir}")
    print(f"{'='*60}")

    generate_all_plots(parsers, output_dir)
    export_all_json(parsers, output_dir)

    # Also generate an HTML dashboard
    generate_html_dashboard(parsers, output_dir)

    print(f"\n  ✓ Done! All outputs in: {output_dir}")


# ─── Fallback parser (for experiments using Bash instead of Write) ─

def parse_fallback(history_path: str, workdir_path: str) -> HistoryParser:
    """
    Build a HistoryParser-equivalent from workdir .py files + JSONL timeline.
    For experiments where code was written via Bash heredocs, not Write tool.
    """
    from history_parser import HistoryParser, VersionRecord, Stage

    # Use HistoryParser for basic infra (JSONL parsing, subagent detection)
    # but manually populate version timeline
    parser = HistoryParser(history_path, workdir_path)

    # 1. Collect verified byte counts from text
    parser._verified_byte_counts = parser._collect_verified_bytes()

    # 2. Measure actual files + get their byte sizes
    file_bytes = {}
    wd = Path(workdir_path)
    v_files = sorted(wd.glob("v*.py"), key=lambda f: f.stat().st_mtime)
    for f in v_files:
        try:
            file_bytes[f.name] = len(f.read_bytes())
        except Exception:
            pass

    # 3. Parse JSONL events
    parser._events = parser._parse_jsonl()

    # 4. Parse subagents
    parser._parse_subagents()

    # 5. Build token timeline
    cumulative_tokens = 0
    token_by_line = {}
    turn_by_line = {}
    assistant_count = 0
    for ev in parser._events:
        if ev['type'] == 'assistant':
            assistant_count += 1
            msg = ev['data'].get('message', {})
            usage = msg.get('usage', {})
            cumulative_tokens += usage.get('input_tokens', 0)
            cumulative_tokens += usage.get('output_tokens', 0)
        if ev['line'] in parser._subagent_tokens:
            cumulative_tokens += parser._subagent_tokens[ev['line']]
        token_by_line[ev['line']] = cumulative_tokens
        turn_by_line[ev['line']] = assistant_count

    # 6. Map v*.py files to conversation timeline by timestamp
    # Each file's timestamp is matched to the line where it was last modified
    # We use the JSONL event timestamps to find the closest match
    event_times = []
    for ev in parser._events:
        ts = ev['data'].get('timestamp', '')
        if ts:
            event_times.append((ev['line'], ts))

    def _find_line_for_mtime(mtime: float) -> int:
        """Find the JSONL line closest to a file modification time."""
        # Convert mtime to ISO-like for comparison
        from datetime import datetime, timezone
        mtime_dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
        best_line = 0
        for line, ts_str in event_times:
            try:
                # Parse ISO timestamp like "2026-07-13T20:19:00Z"
                ts_clean = ts_str.replace('Z', '+00:00')
                ev_dt = datetime.fromisoformat(ts_clean)
                if ev_dt <= mtime_dt:
                    best_line = line
            except (ValueError, TypeError):
                pass
        return best_line

    # 7. Build version records
    seen = set()
    for f in sorted(v_files, key=lambda f: f.stat().st_mtime):
        vname_match = re.match(r'(v\d+)', f.name)
        if not vname_match:
            continue
        vname = vname_match.group(1)
        if vname in seen:
            continue
        seen.add(vname)

        mtime = f.stat().st_mtime
        best_line = _find_line_for_mtime(mtime)
        bc = file_bytes.get(f.name, 0)
        ct = token_by_line.get(best_line, cumulative_tokens)
        turn = turn_by_line.get(best_line, assistant_count)
        is_verified = bc in parser._verified_byte_counts

        parser._detailed_versions.append(VersionRecord(
            version_name=vname,
            filename=f.name,
            byte_count=bc,
            history_line=best_line,
            cumulative_tokens=ct,
            conversation_turn=turn,
            timestamp=datetime.fromtimestamp(mtime).isoformat(),
            is_verified=is_verified,
        ))

    # 8. Build trajectory
    parser._build_trajectory()

    # 9. Detect stages
    parser._detect_stages()

    return parser


# ─── Subagent Version Discovery ─────────────────────────────────

def discover_subagent_versions(parser: 'HistoryParser', history_path: str) -> list:
    """
    Scan subagent JSONL files for Write events that the main parser misses.
    Returns a list of {version, bytes, history_line, cumulative_tokens, ...}
    for all subagent-written .py files that represent code-golf attempts.

    Also checks test results (PASS/FAIL) from tool_result content to determine
    which versions actually pass all tests.
    """
    import glob as glob_mod

    uuid_dir = Path(history_path).parent / Path(history_path).stem
    subagents_dir = uuid_dir / 'subagents'
    if not subagents_dir.exists():
        return []

    subagent_versions = []

    for sa_file in sorted(subagents_dir.glob("agent-*.jsonl")):
        meta_file = subagents_dir / f"{sa_file.stem}.meta.json"
        tool_use_id = ''
        agent_desc = ''
        if meta_file.exists():
            try:
                meta = json.loads(meta_file.read_text())
                tool_use_id = meta.get('toolUseId', '')
                agent_desc = meta.get('description', '')[:80]
            except Exception:
                pass

        # Find the spawn line in main history (only works for direct subagents).
        # Nested subagents won't match — use 0 as sentinel for "no direct spawn".
        spawn_line = 0
        for ev in parser._events:
            if ev['type'] == 'assistant':
                for c in ev['data'].get('message', {}).get('content', []):
                    if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('name') == 'Agent':
                        if c.get('id', '') == tool_use_id:
                            spawn_line = ev['line']

        # Read subagent JSONL
        try:
            sa_lines = sa_file.read_text().splitlines()
        except Exception:
            continue

        # First pass: count tokens per line in subagent
        sa_token_by_line = {}
        sa_cum = 0
        for li, line in enumerate(sa_lines):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get('type') == 'assistant':
                usage = d.get('message', {}).get('usage', {})
                sa_cum += usage.get('input_tokens', 0)
                sa_cum += usage.get('output_tokens', 0)
            sa_token_by_line[li] = sa_cum

        # Find Write events
        writes = []
        for li, line in enumerate(sa_lines):
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get('type') != 'assistant':
                continue
            for c in d.get('message', {}).get('content', []):
                if isinstance(c, dict) and c.get('type') == 'tool_use' and c.get('name') == 'Write':
                    fp = c.get('input', {}).get('file_path', '')
                    fn = os.path.basename(fp)
                    content = c.get('input', {}).get('content', '')
                    size = len(content.encode('utf-8')) if content else 0
                    if size > 40 and size < 500:
                        writes.append({
                            'line': li, 'filename': fn, 'bytes': size,
                            'subagent_tokens': sa_token_by_line.get(li, 0),
                        })

        # Second pass: check test results after each write
        for w in writes:
            # Look at following lines for tool_result with test output
            passes = False
            for j in range(w['line'] + 1, min(w['line'] + 15, len(sa_lines))):
                try:
                    d = json.loads(sa_lines[j])
                except json.JSONDecodeError:
                    continue
                if d.get('type') == 'user':
                    for c in d.get('message', {}).get('content', []):
                        if isinstance(c, dict) and c.get('type') == 'tool_result':
                            txt = str(c.get('content', ''))
                            if 'Passed:' in txt and 'Failed:' in txt:
                                # Parse: "Passed: 3, Failed: 0"
                                import re as re_mod
                                pm = re_mod.search(r'Passed:\s*(\d+)', txt)
                                fm = re_mod.search(r'Failed:\s*(\d+)', txt)
                                if pm and fm:
                                    passes = int(fm.group(1)) == 0 and int(pm.group(1)) > 0
                elif d.get('type') == 'assistant':
                    # Also check assistant text for "passes all tests" claims
                    for c in d.get('message', {}).get('content', []):
                        if isinstance(c, dict) and c.get('type') == 'text':
                            txt = c.get('text', '')
                            if re.search(r'(?:pass(?:es|ing|ed)?\s+all\s+tests?|3/3\s+PASS|all\s+\d+\s+pass)', txt, re.IGNORECASE):
                                passes = True

            subagent_versions.append({
                'version': w['filename'].replace('.py', ''),
                'bytes': w['bytes'],
                'spawn_line': spawn_line,
                'passes_tests': passes,
                'agent_desc': agent_desc,
                'filename': w['filename'],
                'subagent_tokens': w.get('subagent_tokens', 0),
            })

    return subagent_versions


def _merge_subagent_trajectory(parser: 'HistoryParser', subagent_versions: list):
    """
    Merge subagent-discovered versions into the parser's trajectory.
    Only adds versions that pass tests and improve the best-so-far.
    """
    if not subagent_versions:
        return

    traj = parser.get_best_bytes_curve()
    if not traj:
        return

    # Get the last trajectory entry for token/turn context
    last = traj[-1]
    best_bytes = last['bytes']

    # Map lines to cumulative tokens for MAIN THREAD ONLY (no subagent tokens).
    # We'll add subagent tokens separately per version.
    main_token_by_line = {}
    cumulative = 0
    for ev in parser._events:
        if ev['type'] == 'assistant':
            msg = ev['data'].get('message', {})
            usage = msg.get('usage', {})
            cumulative += usage.get('input_tokens', 0)
            cumulative += usage.get('output_tokens', 0)
        main_token_by_line[ev['line']] = cumulative

    # Count turns
    turn_count = max(t['conversation_turn'] for t in traj)

    # Add passing subagent versions that beat the best
    added = 0
    for sv in sorted(subagent_versions, key=lambda x: x['bytes']):
        if sv['passes_tests'] and sv['bytes'] < best_bytes:
            if sv['spawn_line'] > 0:
                # Direct subagent: main tokens at spawn + subagent tokens
                main_tokens = main_token_by_line.get(sv['spawn_line'], last['cumulative_tokens'])
                sa_tokens = sv.get('subagent_tokens', 0)
                total_tokens = main_tokens + sa_tokens
            else:
                # Nested subagent: use total cumulative tokens (all accounted for)
                total_tokens = last['cumulative_tokens']
            parser._trajectory.append({
                'version': sv['version'],
                'bytes': sv['bytes'],
                'cumulative_tokens': total_tokens,
                'conversation_turn': turn_count,
                'history_line': sv['spawn_line'],
                'is_verified': True,
                'timestamp': '',
            })
            best_bytes = sv['bytes']
            added += 1

    if added:
        # Sort by bytes descending so the trajectory ends with the best.
        # Subagent results are appended after the main trajectory.
        parser._trajectory.sort(key=lambda t: (t.get('is_verified', False), t.get('cumulative_tokens', 0)))
        # Then rebuild monotonic: keep only points that improve best-so-far
        filtered = []
        best = float('inf')
        for t in parser._trajectory:
            if t['bytes'] < best:
                best = t['bytes']
                filtered.append(t)
        parser._trajectory = filtered


# ─── Correctness Audit ──────────────────────────────────────────

def run_correctness_audit(parser: 'HistoryParser', history_path: str, exp_name: str = '') -> dict:
    """
    Post-process a parsed experiment to detect which best-bytes versions
    are actually correct (pass all tests) vs broken.

    Uses the MODEL'S OWN WORDS (assistant text), NOT test-runner output,
    to determine correctness. Also detects large version regressions as
    implicit failure signals.

    Returns a dict annotating each trajectory entry with a verdict.
    """
    traj = parser.get_best_bytes_curve()
    if not traj:
        return {'trajectory': [], 'last_known_correct': None}

    # Parse JSONL to get assistant text blocks
    with open(history_path) as f:
        lines = f.readlines()

    # Collect assistant text with line numbers
    assistant_texts = []
    tool_results = []  # (line, tool_use_id, text)
    for line_idx, line in enumerate(lines):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get('type') == 'assistant':
            content = d.get('message', {}).get('content', [])
            for c in content:
                if isinstance(c, dict):
                    if c.get('type') == 'text':
                        assistant_texts.append((line_idx, c.get('text', '')))
                    elif c.get('type') == 'tool_use':
                        # Record tool use for regression detection
                        pass
        elif d.get('type') == 'user':
            content = d.get('message', {}).get('content', [])
            for c in content:
                if isinstance(c, dict) and c.get('type') == 'tool_result':
                    tool_results.append((line_idx, c.get('tool_use_id', ''),
                                        str(c.get('content', ''))))

    # Get all Write events for version lookup
    all_versions = parser.get_all_versions()
    version_line_map = {v.history_line: v for v in all_versions}

    # For each trajectory entry, determine correctness
    annotated = []
    last_known_correct = None

    for i, entry in enumerate(traj):
        vname = entry['version']
        vline = entry['history_line']
        bytes_val = entry['bytes']

        # Find the next trajectory entry's line (or end)
        next_line = traj[i+1]['history_line'] if i+1 < len(traj) else None

        # Get model text BEFORE this write (pre-claim)
        pre_text = ""
        for li, txt in assistant_texts:
            if vline - 8 <= li < vline:
                pre_text += txt + " "

        # Get model text AFTER this write until next best version
        post_text = ""
        for li, txt in assistant_texts:
            if vline < li <= vline + 15:
                post_text += txt + " "

        combined = pre_text + " " + post_text

        # ── Explicit positive signals (model says it passes) ──
        pos_patterns = [
            r'(?:pass(?:es|ing|ed)?\s+all\s+tests?)',
            r'(?:all\s+\d+\s+(?:verification\s+)?(?:cases?\s+)?(?:tests?\s+)?(?:pass|passed))',
            r'(?:(?:\d+\s+)?(?:verification\s+)?(?:cases?|tests?)\s+(?:all\s+)?(?:pass|passed))',
            r'(?:(?:solution|code|this)\s+(?:is\s+)?(?:correct|working)\s*[.!])',
            r'(?:final\s+(?:answer|solution|result|best)[^.]{0,30}\d+\s*bytes?)',
        ]
        pos_count = sum(
            len(re.findall(pat, combined, re.IGNORECASE))
            for pat in pos_patterns
        )

        # ── Explicit negative signals (model says it fails) ──
        neg_patterns = [
            r'(?:but|however|unfortunately|alas)[^.]{0,60}?(?:failing|doesn\'?t\s+pass|still\s+broken|not\s+working)',
            r'(?:doesn\'?t|don\'?t|not)\s+(?:pass|work)\s+(?:all\s+tests|correctly)',
            r'(?:still|is)\s+(?:broken|buggy|incorrect)',
            r'(?:close|almost)[^.]{0,40}(?:but|however)[^.]{0,30}?(?:fail|broken|doesn\'?t)',
        ]
        neg_count = sum(
            len(re.findall(pat, combined, re.IGNORECASE))
            for pat in neg_patterns
        )

        # ── Large regression detection ──
        has_large_regression = False
        regression_bytes = 0
        if i + 1 < len(traj):
            next_entry = traj[i+1]
            # Check if there's any version between this one and the next
            # best-so-far that's significantly larger
            pass
        # Simpler: check the very next version (even non-best) for regression
        # We need the full version list for this
        sorted_versions = sorted(all_versions, key=lambda v: v.history_line)
        for j, v in enumerate(sorted_versions):
            if v.history_line == vline and j + 1 < len(sorted_versions):
                next_v = sorted_versions[j+1]
                if next_v.byte_count - bytes_val > max(20, bytes_val * 0.20):
                    has_large_regression = True
                    regression_bytes = next_v.byte_count - bytes_val
                break

        # Subagent versions are pre-verified by test output (Passed: N, Failed: 0)
        is_subagent_verified = entry.get('is_verified', False) and not re.match(r'v\d+', vname)

        # ── Verdict ──
        # ALSO check: does the parser's verified_byte_counts (global scan)
        # match this version? If the parser found "X bytes ... passes all tests"
        # anywhere in the conversation, and this version's size matches X,
        # that counts as a positive signal.
        parser_verified = bytes_val in getattr(parser, '_verified_byte_counts', set())

        # Refine text-based positive: if the combined text mentions a specific
        # byte count alongside verification claims, only count it as positive
        # if THIS version's size matches that mention.
        # (Prevents v47 from stealing v37's "128 bytes — all pass" claim)
        byte_mention_match = re.findall(
            r'(\d{2,4})\s*bytes?[^.]{0,40}(?:pass(?:es|ing|ed)?|correct|working|verif)',
            combined, re.IGNORECASE
        ) + re.findall(
            r'(?:pass(?:es|ing|ed)?|correct|working|verif)[^.]{0,40}(\d{2,4})\s*bytes?',
            combined, re.IGNORECASE
        )
        if byte_mention_match:
            mentioned_bytes = {int(b) for b in byte_mention_match}
            if bytes_val not in mentioned_bytes:
                # Text mentions a different byte count — don't trust the signal
                text_positive = False
            else:
                text_positive = pos_count > 0
        else:
            text_positive = pos_count > 0

        if is_subagent_verified or ((text_positive or parser_verified) and neg_count == 0):
            verdict = 'correct'
            symbol = '[OK]'
            last_known_correct = {
                'version': vname,
                'bytes': bytes_val,
                'tokens': entry['cumulative_tokens'],
                'turn': entry['conversation_turn'],
            }
        elif neg_count > 0:
            verdict = 'broken'
            symbol = '[FAIL]'
        elif has_large_regression:
            verdict = 'suspicious'
            symbol = '[WARN]'
        else:
            verdict = 'unknown'
            symbol = '[--]'

        annotated.append({
            **entry,
            'verdict': verdict,
            'symbol': symbol,
            'pos_signals': pos_count,
            'neg_signals': neg_count,
            'has_regression': has_large_regression,
            'regression_bytes': regression_bytes,
        })

    # Build "correct-only" trajectory
    correct_trajectory = [a for a in annotated if a['verdict'] == 'correct']

    # PAL-specific: only remove v10 (96B, model said "but failing!").
    # Keep v5 and all other nodes in the trajectory.
    if exp_name == 'PAL':
        parser._trajectory = [t for t in parser._trajectory
                              if t.get('version') != 'v10']

    return {
        'annotated_trajectory': annotated,
        'last_known_correct': last_known_correct,
        'correct_trajectory': correct_trajectory,
    }


def print_correctness_report(name: str, audit: dict):
    """Print a concise correctness summary."""
    traj = audit['annotated_trajectory']
    lkc = audit['last_known_correct']

    broken = [t for t in traj if t['verdict'] == 'broken']
    suspicious = [t for t in traj if t['verdict'] == 'suspicious']
    ct = audit.get('correct_trajectory', [])

    print(f"\n  {name}:")
    if lkc:
        print(f"    Best:  {lkc['bytes']}B ({lkc['version']}, turn {lkc['turn']})")
        if len(ct) > 1:
            parts = [f"{t['version']}:{t['bytes']}B" for t in ct]
            print(f"    Path: {' -> '.join(parts)}")
    else:
        print(f"    Best:  NONE — no version verified as passing")
    if broken:
        for b in broken:
            print(f"    [FAIL] {b['version']} ({b['bytes']}B) — model says it fails")
    if suspicious:
        for s in suspicious:
            print(f"    [WARN] {s['version']} ({s['bytes']}B) — big regression after ({s['regression_bytes']}B)")


# ─── Plotting ─────────────────────────────────────────────────────

def _set_byte_ticks(ax):
    """Custom y-axis: equal visual spacing between all tick marks.

    Ticks: 80, 100, 120, 140, 160, 180, 200 (every 20)
           200, 300, 400, 500, 600, 700, 800 (every 100)

    Each adjacent pair is exactly 1 visual unit apart, achieved via
    piecewise-linear transform: below 200 each 20B = 1 unit,
    above 200 each 100B = 1 unit.
    """
    import numpy as np
    import matplotlib.ticker as ticker

    ticks_lo = np.arange(80, 201, 20)   # 80, 100, ..., 200
    ticks_hi = np.arange(300, 801, 100)  # 300, 400, ..., 800
    all_ticks = np.concatenate([ticks_lo, ticks_hi])

    # Map byte values → display positions
    display_positions = _bytes_to_display(all_ticks)

    ax.set_yticks(display_positions)
    ax.set_yticklabels([f'{int(t)}' for t in all_ticks])
    ax.yaxis.set_minor_locator(ticker.NullLocator())
    ax.set_ylim(_bytes_to_display(np.array([800])), _bytes_to_display(np.array([80])))


def _bytes_to_display(bytes_vals):
    """Piecewise-linear: ≤200 → /20,  >200 → 10 + (val-200)/100."""
    import numpy as np
    vals = np.asarray(bytes_vals, dtype=float)
    result = np.where(
        vals <= 200,
        vals / 20.0,
        10.0 + (vals - 200.0) / 100.0,
    )
    return result


def generate_all_plots(parsers: Dict[str, HistoryParser], out_dir: Path):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not available. pip install matplotlib")
        return

    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 10,
        'axes.titlesize': 13,
        'axes.labelsize': 11,
        'figure.dpi': 150,
    })

    exp_names = list(parsers.keys())
    exp_colors = {
        e['name']: e['color']
        for e in EXPERIMENTS if e['name'] in parsers
    }
    exp_markers = {
        e['name']: e['marker']
        for e in EXPERIMENTS if e['name'] in parsers
    }

    # ── Figure 1: Master dashboard (3×2) ──
    fig, axes = plt.subplots(3, 2, figsize=(20, 18))
    fig.suptitle('Code Golf Experiment — Master Dashboard',
                 fontsize=18, fontweight='bold', y=0.98)
    (ax_tok, ax_turn), (ax_eff, ax_accum), (ax_stage_tok, ax_stage_imp) = axes

    # --- Panel 1: Best bytes vs cumulative tokens ---
    for name, parser in parsers.items():
        traj = parser.get_best_bytes_curve()
        if not traj:
            continue
        color = exp_colors[name]
        tokens = [t['cumulative_tokens'] for t in traj]
        bytes_vals = _bytes_to_display([t['bytes'] for t in traj])
        labels = [t['version'] for t in traj]

        ax_tok.plot(tokens, bytes_vals, '-', color=color, linewidth=2.2,
                    marker=exp_markers[name], markersize=9,
                    markerfacecolor=color, markeredgewidth=1.2,
                    label=name, zorder=5, alpha=0.9)
        ax_tok.fill_between(tokens, bytes_vals, alpha=0.06, color=color)

        for i, (tx, by, lb) in enumerate(zip(tokens, bytes_vals, labels)):
            if i % max(1, len(traj) // 10) == 0 or i == len(traj) - 1:
                ax_tok.annotate(lb, (tx, by), textcoords="offset points",
                                xytext=(0, -14), ha='center', fontsize=6.5,
                                color=color, fontweight='bold', alpha=0.85)

    ax_tok.set_xlabel('Cumulative Tokens')
    ax_tok.set_ylabel('Code Length (bytes)')
    ax_tok.set_title('Bytes vs Tokens')
    ax_tok.legend(loc='upper right', framealpha=0.85, fontsize=9)
    ax_tok.grid(True, alpha=0.2)
    ax_tok.invert_yaxis()
    _set_byte_ticks(ax_tok)

    # --- Panel 2: Best bytes vs conversation turns ---
    for name, parser in parsers.items():
        traj = parser.get_best_bytes_curve()
        if not traj:
            continue
        color = exp_colors[name]
        turns = [t['conversation_turn'] for t in traj]
        bytes_vals = _bytes_to_display([t['bytes'] for t in traj])

        ax_turn.plot(turns, bytes_vals, '-', color=color, linewidth=2.2,
                     marker=exp_markers[name], markersize=9,
                     markerfacecolor=color, markeredgewidth=1.2,
                     label=name, zorder=5, alpha=0.9)
        ax_turn.fill_between(turns, bytes_vals, alpha=0.06, color=color)

    ax_turn.set_xlabel('Conversation Turn')
    ax_turn.set_ylabel('Code Length (bytes)')
    ax_turn.set_title('Bytes vs Turns')
    ax_turn.legend(loc='upper right', framealpha=0.85, fontsize=9)
    ax_turn.grid(True, alpha=0.2)
    ax_turn.invert_yaxis()
    _set_byte_ticks(ax_turn)

    # --- Panel 3: Per-improvement efficiency (Δbytes / kTokens) ---
    bar_width = 0.14
    all_effs = {}
    for name, parser in parsers.items():
        traj = parser.get_best_bytes_curve()
        effs = []
        for i in range(1, len(traj)):
            dbytes = traj[i - 1]['bytes'] - traj[i]['bytes']
            dtokens = traj[i]['cumulative_tokens'] - traj[i - 1]['cumulative_tokens']
            if dtokens > 0 and dbytes > 0:
                effs.append({
                    'label': traj[i]['version'],
                    'efficiency': dbytes / (dtokens / 1000),  # bytes per 1k tokens
                    'dbytes': dbytes,
                })
        all_effs[name] = effs

    # Plot each experiment's efficiency bars as grouped bars
    max_steps = max(len(v) for v in all_effs.values()) if all_effs else 0
    if max_steps > 0:
        x = np.arange(max_steps)
        for j, (name, effs) in enumerate(all_effs.items()):
            color = exp_colors[name]
            vals = [e['efficiency'] for e in effs]
            # pad to same length
            vals += [0] * (max_steps - len(vals))
            offset = (j - len(all_effs) / 2 + 0.5) * bar_width
            bars = ax_eff.bar(x + offset, vals, bar_width * 0.9,
                              color=color, alpha=0.8, label=name,
                              edgecolor='white', linewidth=0.4)
        ax_eff.set_xlabel('Improvement Step')
        ax_eff.set_ylabel('Bytes Saved per 1K Tokens')
        ax_eff.set_title('Improvement Efficiency by Step')
        ax_eff.legend(loc='upper right', framealpha=0.85, fontsize=8)
        ax_eff.grid(True, alpha=0.2, axis='y')
        ax_eff.set_xticks(x)
        ax_eff.set_xticklabels([str(i + 1) for i in range(max_steps)], fontsize=8)

    # --- Panel 4: Token accumulation over turns ---
    for name, parser in parsers.items():
        traj = parser.get_best_bytes_curve()
        if not traj:
            continue
        color = exp_colors[name]
        turns = [t['conversation_turn'] for t in traj]
        tokens = [t['cumulative_tokens'] for t in traj]
        ax_accum.plot(turns, tokens, '-', color=color, linewidth=2.2,
                      marker=exp_markers[name], markersize=7,
                      markerfacecolor=color, markeredgewidth=0.8,
                      label=name, alpha=0.85)
    ax_accum.set_xlabel('Conversation Turn')
    ax_accum.set_ylabel('Cumulative Tokens')
    ax_accum.set_title('Token Accumulation Over Turns')
    ax_accum.legend(loc='lower right', framealpha=0.85, fontsize=9)
    ax_accum.grid(True, alpha=0.2)

    # --- Panel 5: Stage token breakdown (stacked horizontal bars) ---
    stage_data = []
    for name, parser in parsers.items():
        prev_end = 0
        for st in parser.get_stages():
            tokens_here = st.end_tokens - prev_end
            prev_end = st.end_tokens
            stage_data.append({
                'exp': name,
                'stage': st.name,
                'short': st.name.split('. ')[-1][:28],
                'tokens': tokens_here,
                'improvement': st.improvement_bytes,
                'sc': STAGE_COLORS.get(st.name, '#6b7280'),
                'ec': exp_colors[name],
            })

    if stage_data:
        experiments_list = list(parsers.keys())
        stage_names = sorted(set(d['short'] for d in stage_data),
                             key=lambda s: ['Understanding', 'Algorithm',
                                            'Micro', 'Plateau'].index(s)
                             if s in ['Understanding', 'Algorithm',
                                       'Micro', 'Plateau'] else 99)

        y_pos = np.arange(len(experiments_list))
        bar_height = 0.18
        for si, sname in enumerate(stage_names):
            vals = []
            for en in experiments_list:
                match = [d for d in stage_data
                         if d['exp'] == en and d['short'] == sname]
                vals.append(match[0]['tokens'] if match else 0)
            # Find matching stage colour key
            color_keys = [k for k in STAGE_COLORS if sname in k]
            color = STAGE_COLORS[color_keys[0]] if color_keys else '#6b7280'
            if any(v > 0 for v in vals):
                ax_stage_tok.barh(y_pos + si * bar_height, vals,
                                  bar_height * 0.85, label=sname,
                                  color=color,
                                  alpha=0.85, edgecolor='white', linewidth=0.4)

        ax_stage_tok.set_yticks(y_pos + bar_height * (len(stage_names) - 1) / 2)
        ax_stage_tok.set_yticklabels(experiments_list, fontsize=10)
        ax_stage_tok.set_xlabel('Tokens Consumed')
        ax_stage_tok.set_title('Token Consumption by Stage')
        ax_stage_tok.legend(loc='lower right', framealpha=0.85, fontsize=7)
        ax_stage_tok.grid(True, alpha=0.2, axis='x')

    # --- Panel 6: Stage improvement breakdown ---
    if stage_data:
        for si, sname in enumerate(stage_names):
            vals = []
            for en in experiments_list:
                match = [d for d in stage_data
                         if d['exp'] == en and d['short'] == sname]
                vals.append(match[0]['improvement'] if match else 0)
            if any(v > 0 for v in vals):
                ax_stage_imp.barh(y_pos + si * bar_height, vals,
                                  bar_height * 0.85, label=sname,
                                  alpha=0.85, edgecolor='white', linewidth=0.4)

        ax_stage_imp.set_yticks(y_pos + bar_height * (len(stage_names) - 1) / 2)
        ax_stage_imp.set_yticklabels(experiments_list, fontsize=10)
        ax_stage_imp.set_xlabel('Bytes Reduced')
        ax_stage_imp.set_title('Byte Reduction by Stage')
        ax_stage_imp.legend(loc='lower right', framealpha=0.85, fontsize=7)
        ax_stage_imp.grid(True, alpha=0.2, axis='x')

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    p1 = out_dir / 'master_dashboard.png'
    fig.savefig(p1, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  ✓ {p1.name}")

    # ── Figure 2: Comparison summary (raw + verified side-by-side) ──
    fig2, ((ax_final, ax_correct), (ax_total_tok, ax_efficiency)) = plt.subplots(2, 2, figsize=(18, 12))
    fig2.suptitle('Experiment Comparison — Summary Metrics',
                  fontsize=15, fontweight='bold')

    summaries = {name: parser.get_summary() for name, parser in parsers.items()}
    names = list(summaries.keys())
    colors_list = [exp_colors[n] for n in names]

    # Panel 1: Raw best bytes (all versions, may include broken)
    raw_bytes = []
    for n in names:
        s = summaries[n]
        raw_bytes.append(s['final_bytes'] if s else None)
    valid_for_raw = [n for n, b in zip(names, raw_bytes) if b is not None]
    raw_bytes_vals = [b for b in raw_bytes if b is not None]
    raw_colors = [exp_colors[n] for n in valid_for_raw]

    if valid_for_raw:
        bars_fb = ax_final.bar(valid_for_raw, raw_bytes_vals, color=raw_colors, alpha=0.85,
                               edgecolor='white', linewidth=1.5)
        for bar, fb in zip(bars_fb, raw_bytes_vals):
            ax_final.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(raw_bytes_vals)*0.02,
                          f'{fb}B', ha='center', fontsize=11, fontweight='bold')
    ax_final.set_title('Raw Best Bytes (may include broken code)')
    ax_final.set_ylabel('Bytes')
    ax_final.grid(True, alpha=0.2, axis='y')

    # Panel 2: Correctness-verified bytes
    lkc_bytes = []
    lkc_labels = []
    for n in names:
        audit = getattr(parsers[n], '_audit', None)
        if audit and audit['last_known_correct']:
            lkc_bytes.append(audit['last_known_correct']['bytes'])
            lkc_labels.append(audit['last_known_correct']['version'])
        else:
            lkc_bytes.append(0)
            lkc_labels.append('N/A')

    bar_width = 0.35
    x_idx = np.arange(len(names))

    # Side-by-side: raw grey vs verified colored
    raw_vals = [b if b else 0 for b in raw_bytes]
    ax_correct.bar(x_idx - bar_width/2, raw_vals, bar_width,
                   color='#94a3b8', alpha=0.65, label='Raw (may be broken)',
                   edgecolor='white', linewidth=1.2)
    ax_correct.bar(x_idx + bar_width/2, [b if b > 0 else 0 for b in lkc_bytes],
                   bar_width, color=colors_list, alpha=0.9,
                   label='Verified correct',
                   edgecolor='white', linewidth=1.5)

    for i, (bar, fb) in enumerate(zip(
        ax_correct.patches[:len(names)], raw_vals)):
        if fb > 0:
            ax_correct.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                            f'{fb}B', ha='center', fontsize=8, color='#64748b')
    for i, lb in enumerate(lkc_bytes):
        if lb > 0:
            bar = ax_correct.patches[len(names) + i]
            ax_correct.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                            f'{lb}B ({lkc_labels[i]})', ha='center', fontsize=9,
                            fontweight='bold', color=colors_list[i])
        else:
            ax_correct.text(x_idx[i] + bar_width/2, 5,
                            'NONE', ha='center', fontsize=8, color='#ef4444')

    ax_correct.set_xticks(x_idx)
    ax_correct.set_xticklabels(names)
    ax_correct.set_title('Raw vs Verified Bytes')
    ax_correct.set_ylabel('Bytes')
    ax_correct.legend(loc='upper left', framealpha=0.85, fontsize=8)
    ax_correct.grid(True, alpha=0.2, axis='y')

    # Panel 3: Total tokens
    valid_tok_names = [n for n in names if summaries[n]]
    valid_tok = [summaries[n]['total_tokens'] for n in valid_tok_names]
    valid_tok_colors = [exp_colors[n] for n in valid_tok_names]
    if valid_tok_names:
        bars_tt = ax_total_tok.bar(valid_tok_names, valid_tok, color=valid_tok_colors, alpha=0.85,
                                   edgecolor='white', linewidth=1.5)
        for bar, tt in zip(bars_tt, valid_tok):
            ax_total_tok.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(valid_tok)*0.02,
                              f'{tt/1e6:.2f}M', ha='center', fontsize=10, fontweight='bold')
    ax_total_tok.set_title('Total Tokens Consumed')
    ax_total_tok.set_ylabel('Tokens')
    ax_total_tok.grid(True, alpha=0.2, axis='y')

    # Panel 4: Bytes per token efficiency
    valid_bpt_names = [n for n in names if summaries[n]]
    valid_bpt = [summaries[n]['bytes_per_token']*1000 for n in valid_bpt_names]
    valid_bpt_colors = [exp_colors[n] for n in valid_bpt_names]
    if valid_bpt_names:
        bars_bpt = ax_efficiency.bar(valid_bpt_names, valid_bpt, color=valid_bpt_colors, alpha=0.85,
                                     edgecolor='white', linewidth=1.5)
        for bar, bt in zip(bars_bpt, valid_bpt):
            ax_efficiency.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(valid_bpt)*0.02,
                               f'{bt:.2f}', ha='center', fontsize=10, fontweight='bold')
    ax_efficiency.set_title('Overall Efficiency\n(bytes saved / 1K tokens)')
    ax_efficiency.set_ylabel('Bytes per 1K Tokens')
    ax_efficiency.grid(True, alpha=0.2, axis='y')

    plt.tight_layout()
    p2 = out_dir / 'comparison_summary.png'
    fig2.savefig(p2, dpi=150, bbox_inches='tight')
    plt.close(fig2)
    print(f"  ✓ {p2.name}")

    # ── Figure 3: Radar / spider chart (normalized metrics) ──
    try:
        fig3 = plot_radar_comparison(parsers, out_dir, exp_colors)
        print(f"  ✓ radar_comparison.png")
    except Exception as e:
        print(f"  ⚠ Radar chart skipped: {e}")

    # ── Figure 4: Individual experiment trajectory plots ──
    for name, parser in parsers.items():
        try:
            plot_single_experiment(name, parser, out_dir, exp_colors[name])
            print(f"  ✓ {name}_trajectory.png")
        except Exception as e:
            print(f"  ⚠ {name} individual plot failed: {e}")


def plot_radar_comparison(parsers, out_dir, exp_colors):
    import matplotlib.pyplot as plt
    import numpy as np

    summaries = {name: p.get_summary() for name, p in parsers.items()}
    if not summaries:
        return

    names = list(summaries.keys())

    # Metrics (all normalized to 0-1, lower is better for bytes/tokens)
    metrics = ['final_bytes', 'total_tokens', 'total_improvement',
               'total_versions_created', 'total_improvements']

    metric_labels = [
        'Final Bytes\n(lower→better)',
        'Tokens Used\n(lower→better)',
        'Total Bytes\nReduced',
        'Versions\nCreated',
        'Best-Improve\nSteps',
    ]

    # Build raw data
    data = {}
    for name, s in summaries.items():
        data[name] = [s[m] for m in metrics]

    # Normalize: for "lower better" metrics, invert
    all_vals = {m: [summaries[n][m] for n in names] for m in metrics}
    normalized = {}
    for name in names:
        norm = []
        for i, m in enumerate(metrics):
            vals = all_vals[m]
            min_v, max_v = min(vals), max(vals)
            if max_v == min_v:
                norm.append(0.5)
            elif m in ('final_bytes', 'total_tokens'):
                # Lower is better → invert
                norm.append(1.0 - (data[name][i] - min_v) / (max_v - min_v))
            else:
                norm.append((data[name][i] - min_v) / (max_v - min_v))
        normalized[name] = norm

    # Spider plot
    angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
    angles += angles[:1]  # close the circle

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    fig.suptitle('Experiment Comparison — Radar View', fontsize=14, fontweight='bold', y=0.96)

    for name, color in exp_colors.items():
        values = normalized[name] + normalized[name][:1]
        ax.fill(angles, values, alpha=0.08, color=color)
        ax.plot(angles, values, 'o-', linewidth=2.2, color=color,
                label=name, markersize=8)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metric_labels, fontsize=9)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=7)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), framealpha=0.85, fontsize=10)

    plt.tight_layout()
    fig.savefig(out_dir / 'radar_comparison.png', dpi=150, bbox_inches='tight')
    plt.close(fig)


def plot_single_experiment(name, parser, out_dir, color):
    import matplotlib.pyplot as plt
    import numpy as np

    traj = parser.get_best_bytes_curve()
    if not traj:
        return

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'{name} — Verified Trajectory', fontsize=15, fontweight='bold')
    ax1, ax2, ax3, ax4 = axes[0, 0], axes[0, 1], axes[1, 0], axes[1, 1]

    tokens = [t['cumulative_tokens'] for t in traj]
    bytes_vals = _bytes_to_display([t['bytes'] for t in traj])
    turns = [t['conversation_turn'] for t in traj]
    labels = [t['version'] for t in traj]

    # 1. Bytes vs Tokens
    ax1.plot(tokens, bytes_vals, '-o', color=color, linewidth=2.5, markersize=9,
             markerfacecolor=color, markeredgewidth=1.2)
    ax1.fill_between(tokens, bytes_vals, alpha=0.06, color=color)
    for i, (tx, by, lb) in enumerate(zip(tokens, bytes_vals, labels)):
        if i % max(1, len(traj) // 10) == 0 or i == len(traj) - 1:
            ax1.annotate(lb, (tx, by), textcoords="offset points",
                         xytext=(0, -14), ha='center', fontsize=7,
                         color=color, fontweight='bold')
    ax1.set_xlabel('Cumulative Tokens')
    ax1.set_ylabel('Code Length (bytes)')
    ax1.set_title('Bytes vs Tokens')
    ax1.grid(True, alpha=0.2)
    ax1.invert_yaxis()
    _set_byte_ticks(ax1)

    # 2. Bytes vs Turns
    ax2.plot(turns, bytes_vals, '-s', color=color, linewidth=2.5, markersize=9,
             markerfacecolor=color, markeredgewidth=1.2)
    ax2.fill_between(turns, bytes_vals, alpha=0.06, color=color)
    for i, (tx, by, lb) in enumerate(zip(turns, bytes_vals, labels)):
        if i % max(1, len(traj) // 10) == 0 or i == len(traj) - 1:
            ax2.annotate(lb, (tx, by), textcoords="offset points",
                         xytext=(0, -14), ha='center', fontsize=7,
                         color=color, fontweight='bold')
    ax2.set_xlabel('Conversation Turn')
    ax2.set_ylabel('Code Length (bytes)')
    ax2.set_title('Bytes vs Turns')
    ax2.grid(True, alpha=0.2)
    ax2.invert_yaxis()
    _set_byte_ticks(ax2)

    # 3. Token accumulation
    ax3.plot(turns, tokens, '-', color=color, linewidth=2, marker='^', markersize=7)
    ax3.set_xlabel('Conversation Turn')
    ax3.set_ylabel('Cumulative Tokens')
    ax3.set_title('Token Accumulation')
    ax3.grid(True, alpha=0.2)

    # 4. Efficiency bars
    effs = []
    for i in range(1, len(traj)):
        db = traj[i - 1]['bytes'] - traj[i]['bytes']
        dt = traj[i]['cumulative_tokens'] - traj[i - 1]['cumulative_tokens']
        if dt > 0 and db > 0:
            effs.append((traj[i]['version'], db, db / (dt / 1000)))
    if effs:
        x = range(len(effs))
        ax4.bar(x, [e[2] for e in effs], color=color, alpha=0.75,
                edgecolor='white', linewidth=0.5)
        ax4.set_xticks(x)
        ax4.set_xticklabels([f"{e[0]}\n(-{e[1]}B)" for e in effs], fontsize=7)
        ax4.set_xlabel('Improvement Step')
        ax4.set_ylabel('Bytes Saved per 1K Tokens')
        ax4.set_title('Improvement Efficiency')
        ax4.grid(True, alpha=0.2, axis='y')

    plt.tight_layout()
    safe_name = name.lower().replace(' ', '_').replace('-', '_').replace('λ', 'lambda')
    fig.savefig(out_dir / f'{safe_name}_trajectory.png', dpi=150, bbox_inches='tight')
    plt.close(fig)


# ─── JSON Export ─────────────────────────────────────────────────

def export_all_json(parsers: Dict[str, HistoryParser], out_dir: Path):
    export = {}
    for name, parser in parsers.items():
        summary = parser.get_summary()
        traj = parser.get_best_bytes_curve()
        stages = [
            {
                'name': s.name,
                'start_turn': s.start_turn, 'end_turn': s.end_turn,
                'start_tokens': s.start_tokens, 'end_tokens': s.end_tokens,
                'best_bytes_start': s.best_bytes_start,
                'best_bytes_end': s.best_bytes_end,
                'improvement_bytes': s.improvement_bytes,
                'description': s.description,
            }
            for s in parser.get_stages()
        ]
        versions = [
            {
                'version': v.version_name,
                'byte_count': v.byte_count,
                'cumulative_tokens': v.cumulative_tokens,
                'conversation_turn': v.conversation_turn,
                'is_verified': v.is_verified,
                'timestamp': v.timestamp,
            }
            for v in parser.get_all_versions()
        ]

        # Include correctness audit
        audit = getattr(parser, '_audit', None)
        audit_export = None
        if audit:
            audit_export = {
                'last_known_correct': audit['last_known_correct'],
                'annotated_trajectory': [
                    {k: v for k, v in a.items() if k in (
                        'version', 'bytes', 'cumulative_tokens', 'conversation_turn',
                        'verdict', 'symbol', 'pos_signals', 'neg_signals',
                        'has_regression', 'regression_bytes',
                    )}
                    for a in audit['annotated_trajectory']
                ],
            }

        export[name] = {
            'summary': summary,
            'trajectory': traj,
            'stages': stages,
            'all_versions': versions,
            'correctness_audit': audit_export,
        }

    path = out_dir / 'all_experiments.json'
    with open(path, 'w') as f:
        json.dump(export, f, indent=2, default=str)
    print(f"  ✓ {path.name}")


# ─── HTML Dashboard ──────────────────────────────────────────────

def generate_html_dashboard(parsers: Dict[str, HistoryParser], out_dir: Path):
    """Generate a self-contained HTML dashboard with Chart.js."""

    summaries = {name: p.get_summary() for name, p in parsers.items()}
    exp_colors = {e['name']: e['color'] for e in EXPERIMENTS if e['name'] in parsers}

    # Build y-axis tick mapping for piecewise-linear transform
    import numpy as np
    ticks_lo = np.arange(80, 201, 20)
    ticks_hi = np.arange(300, 801, 100)
    all_ticks = np.concatenate([ticks_lo, ticks_hi])
    tick_positions = _bytes_to_display(all_ticks)
    y_ticks_json = json.dumps([
        [float(pos), int(label)]
        for pos, label in zip(tick_positions, all_ticks)
    ])

    # Serialise trajectory data for JS (with transformed bytes + correctness audit)
    datasets_json = {}
    for name, parser in parsers.items():
        traj = parser.get_best_bytes_curve()
        raw_bytes = [t['bytes'] for t in traj]

        # Get correctness verdicts for each trajectory point
        audit = getattr(parser, '_audit', None)
        verdict_map = {}
        lkc = None
        if audit:
            for a in audit['annotated_trajectory']:
                verdict_map[a['version']] = a['verdict']
            lkc = audit['last_known_correct']

        verdicts = [verdict_map.get(t['version'], 'unknown') for t in traj]

        datasets_json[name] = {
            'tokens': [t['cumulative_tokens'] for t in traj],
            'bytes': [float(b) for b in _bytes_to_display(raw_bytes)],
            'raw_bytes': raw_bytes,
            'turns': [t['conversation_turn'] for t in traj],
            'versions': [t['version'] for t in traj],
            'verdicts': verdicts,
            'last_known_correct': lkc,
            'stages': [
                {
                    'name': s.name,
                    'end_tokens': s.end_tokens,
                    'end_turn': s.end_turn,
                    'improvement': s.improvement_bytes,
                    'description': s.description,
                }
                for s in parser.get_stages()
            ],
            'summary': summaries[name],
        }

    colors_json = json.dumps(exp_colors)
    datasets_json_str = json.dumps(datasets_json)

    gen_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    n_exp = len(parsers)

    # Write the HTML via a helper to avoid f-string vs JS brace hell
    html = _build_html(gen_time, n_exp, colors_json, datasets_json_str, y_ticks_json)

    path = out_dir / 'dashboard.html'
    path.write_text(html)
    print(f"  ✓ {path.name}")


def _build_html(gen_time: str, n_exp: int, colors_json: str, datasets_json_str: str, y_ticks_json: str) -> str:
    """Build HTML dashboard string, avoiding f-string vs JS brace conflicts."""

    # Use sentinel replacement to keep JS braces untouched
    tmpl = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Code Golf — History Visualizations</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js">
</script>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #f8fafc; color: #1e293b; padding: 24px; }
h1 { font-size: 28px; margin-bottom: 8px; }
.subtitle { color: #64748b; margin-bottom: 32px; font-size: 15px; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(620px, 1fr));
        gap: 24px; }
.card { background: #fff; border-radius: 14px; padding: 22px;
        box-shadow: 0 1px 3px rgba(0,0,0,.07); border: 1px solid #e2e8f0; }
.card h2 { font-size: 16px; margin-bottom: 14px; color: #334155; }
.chart-wrap { position: relative; width: 100%; }
.chart-wrap canvas { width: 100% !important; }
.summary-table { width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 16px; }
.summary-table th, .summary-table td { padding: 8px 12px; text-align: right;
    border-bottom: 1px solid #e2e8f0; }
.summary-table th:first-child, .summary-table td:first-child { text-align: left; font-weight: 600; }
.summary-table tr:last-child td { border-bottom: none; }
.badge { display: inline-block; padding: 2px 8px; border-radius: 6px;
         font-size: 12px; font-weight: 600; }
.badge-best { background: #dcfce7; color: #166534; }
</style>
</head>
<body>

<h1>🏌️ Code Golf — Experiment History Dashboard</h1>
<p class="subtitle">Generated __GEN_TIME__ · __N_EXP__ experiments</p>

<div class="card" style="margin-bottom:24px;">
<h2>📊 Summary Table</h2>
<div id="summary-table"></div>
</div>

<div class="grid">
  <div class="card"><h2>📉 Best Bytes vs Tokens</h2>
    <div class="chart-wrap"><canvas id="bytesVsTokens"></canvas></div></div>
  <div class="card"><h2>📉 Best Bytes vs Turns</h2>
    <div class="chart-wrap"><canvas id="bytesVsTurns"></canvas></div></div>
  <div class="card"><h2>📈 Token Accumulation</h2>
    <div class="chart-wrap"><canvas id="tokenAccum"></canvas></div></div>
  <div class="card"><h2>⚡ Final Bytes Comparison</h2>
    <div class="chart-wrap"><canvas id="finalBytes"></canvas></div></div>
  <div class="card"><h2>🔬 Stage Analysis — Tokens</h2>
    <div class="chart-wrap"><canvas id="stageTokens"></canvas></div></div>
  <div class="card"><h2>🔬 Stage Analysis — Improvements</h2>
    <div class="chart-wrap"><canvas id="stageImprove"></canvas></div></div>
</div>

<script>
var COLORS = __COLORS_JSON__;
var DATA = __DATASETS_JSON__;
var Y_TICKS = __Y_TICKS__;
var EXP_NAMES = Object.keys(DATA);

// Piecewise-linear y-axis: use Y_TICKS [[pos,label],...] for byte charts
function bytesToDisplay(v) {
  return v <= 200 ? v / 20.0 : 10.0 + (v - 200.0) / 100.0;
}
function byteYaxis() {
  return {
    type: 'linear',
    title: { display: true, text: 'Best Bytes' },
    ticks: {
      stepSize: 1,
      callback: function(val) {
        for (var i = 0; i < Y_TICKS.length; i++) {
          if (Math.abs(Y_TICKS[i][0] - val) < 0.01) return Y_TICKS[i][1];
        }
        return '';
      }
    },
    afterBuildTicks: function(axis) {
      axis.ticks = Y_TICKS.map(function(t) { return { value: t[0] }; });
    }
  };
}

Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
Chart.defaults.font.size = 12;

function makeChart(id, config) {
  var ctx = document.getElementById(id).getContext('2d');
  new Chart(ctx, config);
}

// Summary table
(function() {
  var div = document.getElementById('summary-table');
  var metrics = [
    {key:'initial_bytes', label:'Initial Bytes'},
    {key:'final_bytes', label:'Final Bytes'},
    {key:'total_improvement', label:'Total Improvement'},
    {key:'improvement_pct', label:'Improvement %', suffix:'%'},
    {key:'total_tokens', label:'Total Tokens', fmt:'comma'},
    {key:'total_versions_created', label:'Versions Created'},
    {key:'total_improvements', label:'Best-Improve Steps'},
    {key:'bytes_per_token', label:'Bytes/Token', fmt:'.4f'},
  ];
  var html = '<table class="summary-table"><thead><tr><th>Metric</th>';
  for (var i = 0; i < EXP_NAMES.length; i++) html += '<th>' + EXP_NAMES[i] + '</th>';
  html += '</tr></thead><tbody>';

  for (var mi = 0; mi < metrics.length; mi++) {
    var m = metrics[mi];
    html += '<tr><td>' + m.label + '</td>';
    var vals = EXP_NAMES.map(function(n) { return DATA[n].summary[m.key]; });
    var best;
    if (m.key === 'final_bytes' || m.key === 'total_tokens') {
      best = Math.min.apply(null, vals.filter(function(v) { return v > 0; }));
    } else {
      best = Math.max.apply(null, vals);
    }
    for (var ni = 0; ni < EXP_NAMES.length; ni++) {
      var n = EXP_NAMES[ni];
      var v = DATA[n].summary[m.key];
      var cls = (v === best && vals.filter(function(x){return x===v;}).length===1) ? 'badge-best' : '';
      if (m.fmt === 'comma') v = Number(v).toLocaleString();
      else if (m.fmt) v = Number(v).toFixed(4);
      if (m.suffix) v += m.suffix;
      html += '<td>' + (cls ? '<span class="badge ' + cls + '">' + v + '</span>' : v) + '</td>';
    }
    html += '</tr>';
  }
  html += '</tbody></table>';

  // Add "Best Verified Correct" row
  html += '<br><table class="summary-table"><thead><tr><th>Best Verified Correct</th>';
  for (var ni = 0; ni < EXP_NAMES.length; ni++) html += '<th>' + EXP_NAMES[ni] + '</th>';
  html += '</tr></thead><tbody><tr><td>Bytes (version)</td>';
  for (var ni = 0; ni < EXP_NAMES.length; ni++) {
    var n = EXP_NAMES[ni];
    var lkc = DATA[n].last_known_correct;
    if (lkc) {
      html += '<td><span class="badge badge-best">' + lkc.bytes + 'B (' + lkc.version + ')</span></td>';
    } else {
      html += '<td><span class="badge badge-worst">NONE</span></td>';
    }
  }
  html += '</tr></tbody></table>';

  div.innerHTML = html;
})();

function makeTrajectoryDataset(name) {
  var d = DATA[name];
  return {
    label: name,
    data: d.tokens.map(function(t, i) { return {x: t, y: d.bytes[i]}; }),
    borderColor: COLORS[name],
    backgroundColor: COLORS[name],
    showLine: true,
    tension: 0.1,
    pointRadius: 5,
    pointHoverRadius: 8,
    borderWidth: 2,
  };
}

// Bytes vs Tokens
makeChart('bytesVsTokens', {
  type: 'scatter',
  data: {
    datasets: EXP_NAMES.map(function(name) { return makeTrajectoryDataset(name); }),
  },
  options: {
    responsive: true,
    scales: {
      x: { title: {display: true, text: 'Cumulative Tokens'} },
      y: byteYaxis(),
    },
    plugins: { tooltip: { callbacks: {
      label: function(ctx) {
        var d = DATA[ctx.dataset.label];
        var raw = d.raw_bytes[ctx.dataIndex];
        return d.versions[ctx.dataIndex] + ': ' + raw + ' bytes';
      }
    }}}
  }
});

// Bytes vs Turns
makeChart('bytesVsTurns', {
  type: 'scatter',
  data: {
    datasets: EXP_NAMES.map(function(name) {
      var d = DATA[name];
      return {
        label: name,
        data: d.turns.map(function(t, i) { return {x: t, y: d.bytes[i]}; }),
        borderColor: COLORS[name],
        backgroundColor: COLORS[name],
        showLine: true,
        tension: 0.1,
        pointRadius: 5,
        pointHoverRadius: 8,
        borderWidth: 2,
      };
    }),
  },
  options: {
    responsive: true,
    scales: {
      x: { title: {display: true, text: 'Conversation Turn'} },
      y: byteYaxis(),
    },
    plugins: { tooltip: { callbacks: {
      label: function(ctx) {
        var raw = DATA[ctx.dataset.label].raw_bytes[ctx.dataIndex];
        return DATA[ctx.dataset.label].versions[ctx.dataIndex] + ': ' + raw + ' bytes';
      }
    }}}
  }
});

// Token accumulation
makeChart('tokenAccum', {
  type: 'scatter',
  data: {
    datasets: EXP_NAMES.map(function(name) {
      return {
        label: name,
        data: DATA[name].turns.map(function(t, i) { return {x: t, y: DATA[name].tokens[i]}; }),
        borderColor: COLORS[name],
        backgroundColor: COLORS[name],
        showLine: true,
        tension: 0.1,
        pointRadius: 4,
        pointHoverRadius: 7,
        borderWidth: 2,
      };
    }),
  },
  options: {
    responsive: true,
    scales: {
      x: { title: {display: true, text: 'Conversation Turn'} },
      y: { title: {display: true, text: 'Cumulative Tokens'} },
    },
  }
});

// Final Bytes bar
makeChart('finalBytes', {
  type: 'bar',
  data: {
    labels: EXP_NAMES,
    datasets: [{
      label: 'Final Bytes',
      data: EXP_NAMES.map(function(n) { return bytesToDisplay(DATA[n].summary.final_bytes); }),
      backgroundColor: EXP_NAMES.map(function(n) { return COLORS[n] + '99'; }),
      borderColor: EXP_NAMES.map(function(n) { return COLORS[n]; }),
      borderWidth: 2,
    }],
  },
  options: {
    responsive: true,
    scales: { y: byteYaxis() },
    plugins: { legend: { display: false },
      tooltip: { callbacks: {
        label: function(ctx) {
          var raw = DATA[ctx.label].summary.final_bytes;
          return raw + ' bytes';
        }
      }}
    }
  }
});

// Stage breakdown
(function() {
  var stageNames = ['1. Understanding & First Solution', '2. Algorithm Exploration',
                     '3. Micro-Optimization (Golfing)', '4. Plateau / Converged'];
  var stageColors = ['#f59e0b', '#3b82f6', '#8b5cf6', '#ef4444'];

  var tokDatasets = stageNames.map(function(sn, si) {
    return {
      label: sn.split('. ')[1],
      data: EXP_NAMES.map(function(n) {
        var stages = DATA[n].stages;
        for (var i = 0; i < stages.length; i++) {
          if (stages[i].name === sn) {
            var prevEnd = i > 0 ? stages[i-1].end_tokens : 0;
            return stages[i].end_tokens - prevEnd;
          }
        }
        return 0;
      }),
      backgroundColor: stageColors[si] + 'bb',
      borderColor: stageColors[si],
      borderWidth: 1,
    };
  });

  makeChart('stageTokens', {
    type: 'bar',
    data: { labels: EXP_NAMES, datasets: tokDatasets },
    options: {
      responsive: true,
      scales: { x: { stacked: true }, y: { stacked: true, title: {display: true, text: 'Tokens'} } },
    }
  });

  var impDatasets = stageNames.map(function(sn, si) {
    return {
      label: sn.split('. ')[1],
      data: EXP_NAMES.map(function(n) {
        var stages = DATA[n].stages;
        for (var i = 0; i < stages.length; i++) {
          if (stages[i].name === sn) return stages[i].improvement;
        }
        return 0;
      }),
      backgroundColor: stageColors[si] + 'bb',
      borderColor: stageColors[si],
      borderWidth: 1,
    };
  });

  makeChart('stageImprove', {
    type: 'bar',
    data: { labels: EXP_NAMES, datasets: impDatasets },
    options: {
      responsive: true,
      scales: { x: { stacked: true }, y: { stacked: true, title: {display: true, text: 'Bytes Reduced'} } },
    }
  });
})();
</script>
</body>
</html>"""

    return (tmpl
            .replace('__GEN_TIME__', gen_time)
            .replace('__N_EXP__', str(n_exp))
            .replace('__COLORS_JSON__', colors_json)
            .replace('__DATASETS_JSON__', datasets_json_str)
            .replace('__Y_TICKS__', y_ticks_json))


# ─── Entry point ──────────────────────────────────────────────────

if __name__ == '__main__':
    main()
