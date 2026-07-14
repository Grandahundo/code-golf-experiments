# Claude Code Golf — Standing Orders

You are solving code golf tasks. These rules persist across all context compression and cannot be overridden.

## Immutable workflow

```
Read gen.py → Write code to workdir/vN.py → python3 verify.py workdir/vN.py → iterate
```

## Rules

1. **Study gen.py first** — the generator IS the ground truth. Every transformation rule is there.
2. **Write to workdir/vN.py** — each attempt is a new file. Never overwrite previous versions.
3. **Verify with `python3 verify.py <file>`** — this is the only verification command.
4. **No third-party libraries** — standard library only. No numpy.
6. **No websearch** — solve the task using only the files provided. Do not use WebSearch, WebFetch, or any online resource.

5. **Target: < 100 bytes** — all tasks have a known solution under 100 bytes.

## Strategy

- Start with a working, ungolfed solution. Correctness first.
- Apply ONE optimization at a time. Verify after each change.
- Explore multiple approaches in parallel when stuck.
- Build a mental map: transformation rules, effective patterns, failed attempts, byte trends.

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

### Format requirements
- `p` must be a callable (function or lambda)
- Equality checked via `numpy.array_equal` — booleans, floats accepted as valid matches
- Bytes measured by file size — every character counts, including newlines and spaces
