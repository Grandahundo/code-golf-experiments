# Code Golf Task 004 — PAL Cognitive Framework

You are solving Task 004 in this code golf competition. The task data is in `data.json`. Your goal: the shortest Python 3 file defining a callable `p` that correctly maps each input matrix to its output matrix. All values are integers 0–9, structured as nested lists. Third-party libraries (`numpy`, etc.) are forbidden. Equality is checked via `numpy.array_equal` — booleans, floats, and compatible types are accepted as long as values align. Length is measured in bytes. All tasks have a solution under 100 bytes; most under 80.

## CRITICAL: You operate within a structured framework

This directory contains `cognitive_map.py` — an **executable Python module** that serves as your thinking skeleton, state machine, version tracker, and knowledge database. You do NOT work in free-form prose. All state persists to `workdir/*.json` and survives context truncation.

### Startup (do this FIRST on every conversation)

```bash
python3 -c "from cognitive_map import *; print(status())"
```

This prints your current state, allowed actions, version tree, and best attempt so far.

### State flow (cannot skip steps):

```
INIT → ANALYZE_GEN → WRITE_CODE → VERIFY → GOLF → VERIFY → ... → DONE
```

## First Priority: Study the Dataset Generator

The generator at `gen.py` defines the exact transformation logic. **Read it fully before writing any code.** It reveals core patterns, edge cases, and hidden invariants you will never discover from sample pairs alone. If stuck, return to it — this saves far more time than blind trial-and-error.

## Map-and-Act Strategy

Throughout your work, **simultaneously build a structured cognitive map** via `learn()`. Your map should cover:

- **Core generator logic**: transformation rules, color mappings, shape constraints, boundary conditions, hidden invariants. Record code snippets or pseudocode.
- **Verification behavior**: how `verify.py` checks correctness, measures bytes, implicit type conversions accepted.
- **Database of effective patterns**: Python golf techniques proven to pass, with exact byte savings.
- **Failed attempts**: error messages, off-by-one bugs, type mismatches, constraints that caused failures.
- **Byte-count trends**: how much each optimization saved, conflicts between optimizations.

Record knowledge as you discover it — structured, not lost:

```bash
python3 -c "
from cognitive_map import *
learn(
    transformation_type='parallelogram_shift',
    transformation_params={'direction': 'right', 'amount': 1},
    rules=[
        'top edge shifts right by 1 pixel',
        'left diagonal shifts right by 1 pixel',
        'bottom edge stays in place'
    ],
    invariants=['grid dimensions unchanged', 'color values preserved'],
    confidence=0.9
)
"
```

### Use the map strategically:
1. **Consult before each attempt** — review confirmed rules, avoid repeating mistakes.
2. **Update after every verify** — extract new observations immediately.
3. **Guide parallel exploration** — when using agent team, assign each member a distinct hypothesis from your map.
4. **Pivot, don't brute-force** — if stuck, review the map for overlooked patterns.
5. **Keep it concise** — prune outdated entries, keep justifications and code snippets.

## Explore Multiple Approaches in Parallel

Don't fixate on one approach. Use **the agent team feature** to run distinct strategies concurrently — different logical patterns, syntax shortcuts, implementation styles. The optimal solution is shorter than you expect.

## Prioritize Correctness, Optimize Incrementally

**Start with a working, ungolfed solution** that passes all tests. Then apply ONE optimization at a time. Verify after each change. Never trade correctness for shorter code.

## Submitting Code

Code goes through `submit()` — the ONLY way to record attempts. Always write candidate code to a file in `workdir/` first (e.g., `workdir/vN.py`):

```bash
python3 -c "
from cognitive_map import *
a = submit(
    code=open('workdir/vN.py').read(),
    parent='v1',
    insight='applied list comprehension, saved 15 bytes'
)
print(f'passed={a.passed} bytes={a.bytes}')
"
```

This enforces constraints → runs verify.py → adds to DAG → auto-saves to disk. Both passing AND failing attempts are recorded.

## Version Logging

Every attempt is automatically logged in the DAG (`workdir/dag.json`). You should also maintain brief notes for each version:

- **Intuition**: the reasoning behind the change
- **Code**: the full implementation
- **Bytes**: code length
- **Saved**: bytes saved vs parent version

These are captured in the `insight` field of `submit()` and persisted in the DAG. For deeper notes, write to `workdir/insights.md`.

## Check Progress

```bash
python3 -c "from cognitive_map import *; print(status()); print('Trend:', trend())"
```

## Rules

- First action: read and understand `gen.py`
- Work inside `workdir/` — create a new file per attempt, never overwrite previous versions
- All code goes through `submit()` — NEVER run verify.py manually
- All knowledge goes through `learn()` — structured, persisted, queryable
- The DAG at `workdir/dag.json` is your source of truth across sessions
- Work independently — use your best judgment, don't ask for guidance
- Record results honestly — false claims will be caught by verify.py
- Stop when `best().bytes < 100`
