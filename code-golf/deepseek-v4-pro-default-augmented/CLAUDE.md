# Code Golf Task Guide

You are solving Task 004. Goal: shortest `p` function, target < 100 bytes. All values are integers 0–9. Equality checked via `numpy.array_equal` — booleans, floats accepted. No third-party libraries. All tasks have a known solution under 100 bytes; most under 80.


## Immutable workflow

```
Read gen.py → Write code to workdir/vN.py → python3 verify.py workdir/vN.py → iterate
```

## First Priority: Study gen.py

The generator at `gen.py` defines the exact transformation logic. Read it fully before writing any code. It reveals core patterns, edge cases, and hidden invariants you will never discover from sample pairs alone. Return to it whenever stuck — this saves far more time than blind trial-and-error.

## Explore Multiple Approaches in Parallel

Don't fixate on one approach. Use the agent team to run distinct strategies concurrently — different logical patterns, different syntax shortcuts, different implementation styles. The optimal solution is shorter than you expect.

## Map-and-Act Strategy

Maintain a cognitive map throughout your work. Update it after each verification.

Cover these categories:
- **Core generator logic**: transformation rules, color mappings, shape constraints, boundary conditions, hidden invariants
- **Verification behavior**: how correctness is checked, byte measurement, implicit type conversions
- **Effective patterns**: Python golf techniques that pass, with exact byte savings
- **Failed attempts**: error messages, off-by-one bugs, type mismatches
- **Byte-count trends**: savings per optimization, conflicts between optimizations

Use the map: consult before each attempt, update after each verify, guide parallel explorations, pivot when stuck.

## Prioritize Correctness, Optimize Incrementally

Start with a working, ungolfed solution. Apply ONE optimization at a time. Verify after each change. Never trade correctness for shorter code.

## Code Golf Techniques

### Prefer recursion over loops
Recursion compresses iteration into fewer characters. A recursive call can replace nested `for` loops, especially for grid traversals and flood-fill:

```python
# Loop (long):
for r in range(H):
    for c in range(W):
        if g[r][c]: f(r,c)

# Recursive (short):
def p(g,i=0):r=i//W;c=i%W;return i<H*W and(...or p(g,i+1))
```

### Lambda-first approach
Lambda is almost always shorter than `def`+`return`. Target: `p=lambda g:<expr>`.

Multi-statement packing techniques:
```python
# Tuple trick for multi-step:
p=lambda g:(s:={*...},[s.add(x)for x in...],...)[-1]

# Walrus in comprehension:
p=lambda g:[c for r in g for c in r if(c:=f(r))]

# Short-circuit instead of if/else:
p=lambda g:g and f(g)or 0

# exec for complex multi-statement logic:
p=lambda g,exec('...'):eval('...')
```

### Other patterns
- `[*map(f,x)]` — compare bytes vs list comprehension case-by-case
- Unpacking: `*x,=f()` shorter than `x[0]`
- Semicolons chain statements on one line
- Single-letter names: `g`=grid, `r`/`c`=row/col, `h`/`w`=height/width, `i`/`j`=indices
- Negative indices: `g[-1]` not `g[len(g)-1]`
- `!=0` can often be dropped (truthy check): `if g[r][c]` not `if g[r][c]!=0`

## Working Requirements
- Work independently — don't ask for guidance
- Write each attempt to `workdir/vN.py` — new file per attempt, never overwrite
- Verify with `python3 verify.py workdir/vN.py` — the only verification command
- Keep notes in `workdir/insights.md`
- Stop when under 100 bytes
