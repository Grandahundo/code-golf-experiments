# Code Golf Task 004 — PAL + Lambda Framework

You are solving Task 004. Goal: the shortest `p` function that passes verify.py, target < 100 bytes.

## Core Strategy: Lambda-First

**Use `p=lambda` as your default.** A lambda expression is almost always shorter than `def p(...):` + `return`. Your final solution should be a single lambda where possible.

### Lambda patterns to master:

```python
# Basic: p as lambda
p=lambda g:[[...for c in r]for r in g]

# Multi-statement via tuple/and/or tricks:
p=lambda g:(s:={...},[s.add(...)for r in g],...)[-1]

# Conditional with and/or (shorter than if/else):
p=lambda g:g and f(g)or 0

# Walrus operator for state inside comprehension:
p=lambda g:[c for r in g for c in r if(c:=f(r))]

# exec for complex logic packed into lambda:
p=lambda g,exec('...'):eval('...')

# Nested lambdas for multi-pass transforms:
p=lambda g:(lambda h:...)([[...for c in r]for r in g])

# Map/filter for character savings:
p=lambda g:[*map(lambda r:[*filter(bool,r)],g)]
```

### Target format:
```python
p=lambda g:<single-expression>
```

If impossible as pure lambda, use the shortest `def` you can, then golf back toward lambda.

## CRITICAL: Structured framework

You work within `cognitive_map.py`. Startup:

```bash
python3 -c "from cognitive_map import *; print(status())"
```

### State flow:
```
INIT → ANALYZE_GEN → WRITE_CODE → VERIFY → GOLF → VERIFY → ... → DONE
```

### Record knowledge:
```bash
python3 -c "
from cognitive_map import *
learn(
    transformation_type='parallelogram_shift',
    transformation_params={'direction': 'right', 'amount': 1},
    rules=['top edge shifts right by 1', 'left diagonal shifts right by 1'],
    invariants=['grid dimensions unchanged'],
    confidence=0.9
)
"
```

### Submit code:
```bash
python3 -c "
from cognitive_map import *
a = submit(code=open('workdir/vN.py').read(), parent='v1',
    insight='converted to lambda, saved 40 bytes')
print(f'passed={a.passed} bytes={a.bytes}')
"
```

### Check progress:
```bash
python3 -c "from cognitive_map import *; print(status()); print('Trend:', trend())"
```

## Lambda Golfing Tips

| Technique | Example | Saves |
|-----------|---------|-------|
| `p=lambda g:` vs `def p(g):`+`return` | 10→8 chars | ~15-20 bytes |
| Walrus `:=` for temp vars | `(s:=f(x),g(s))[-1]` | ~10-15 bytes |
| `[*map(...)]` vs `[f(x)for x in...]` | case-by-case | ~2-5 bytes |
| `and`/`or` short-circuit vs `if`/`else` | `x and y or z` | ~5-10 bytes |
| Unpacking `*x,` vs `x[0]` | `*x,=f()` | ~3-5 bytes |
| `exec` for multi-statement packing | `exec('...')` | varies |

## First Priority: Study gen.py

Read `gen.py` fully before writing any code. The transformation logic is there — lambda tricks are useless if you don't understand the problem.

## Rules
- Default to lambda. Use `def` only when lambda is impossible.
- All code through `submit()` — never bypass.
- All knowledge through `learn()`.
- Work inside `workdir/`.
- Stop when `best().bytes < 100`.
