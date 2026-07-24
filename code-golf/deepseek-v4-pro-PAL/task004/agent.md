# Code Golf Task 004 — PAL Cognitive Framework

You are solving Task 004. Goal: shortest `p` function that passes verify.py, target < 100 bytes.

## CRITICAL: Structured framework

You work within `cognitive_map.py` — an executable module that enforces state, tracks versions in a DAG, and persists everything to `workdir/`. You do NOT work in free-form prose. All state survives context truncation via JSON files on disk.

## Startup (do this FIRST)

```bash
python3 -c "from cognitive_map import *; print(status())"
```

This prints your current state, allowed actions, version tree, and best attempt.

## How you work

### State flow (cannot skip):
```
INIT → ANALYZE_GEN → WRITE_CODE → VERIFY → GOLF → VERIFY → ... → DONE
```

### Record structured knowledge (not prose):
```bash
python3 -c "
from cognitive_map import *
learn(
    transformation_type='shift',
    transformation_params={'direction': 'right', 'amount': 1},
    rules=['top edge shifts right by 1'],
    confidence=0.8
)
"
```

### Submit code (the ONLY way to record attempts):
```bash
python3 -c "
from cognitive_map import *
a = submit(
    code=open('workdir/vN.py').read(),
    parent='v1',
    insight='what you changed and why'
)
print(f'passed={a.passed} bytes={a.bytes}')
"
```
This enforces constraints → runs verify.py → adds to DAG → saves to disk. Always write the candidate code to a file first (e.g., `workdir/vN.py`).

### Check progress any time:
```bash
python3 -c "from cognitive_map import *; print(status()); print('Trend:', trend())"
```

## Rules
- First action: read and understand `gen.py`
- Always work inside `workdir/` for your code files
- Every attempt goes through `submit()` — NEVER run verify.py manually
- All knowledge goes through `learn()` — structured, persisted, never lost
- The DAG at `workdir/dag.json` is your source of truth across sessions
- Stop when `best().bytes < 100`
