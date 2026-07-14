# Task 004 Insights

## Problem Understanding
- Each shape is a parallelogram with UNIQUE color (colors 1-9 sampled without replacement)
- Transformation from generator (gen.py): top edge and left diagonal shift right by 1, bottom edge stays, right diagonal shifts right by 1 but clamped to shape's rightmost column (col+wide-1)
- Because each color = one shape, per-color tracking is equivalent to per-shape tracking

## Transformation Rule
For each non-zero pixel at (r,c) with color v:
1. Find max_col[v] = rightmost column of color v (always in bottom row)
2. Find max_row[v] = last row of color v (bottom row)
3. If r == max_row[v] OR c == max_col[v]: stay at (r,c)
4. Else: shift to (r, c+1)

## Best Solution (v29, 156 bytes)
Top-to-bottom approach: pair each row with row below, compute per-row max_col dict.
- `zip(g,g[1:])` pairs adjacent rows
- `{v:c for c,v in enumerate(b)if v}` maps color→rightmost_col for row below
- Process each row right-to-left: shift if `c < m.get(v,-1)`

## Key Optimizations Applied
1. `zip(g,g[1:])` instead of index-based iteration (saves ~13 bytes)
2. `[*enumerate(r)][::-1]` instead of `range(len(r)-1,-1,-1)` + indexing (saves ~9 bytes)
3. Slice assignment `r[c:c+2]=0,v` instead of `r[c]=0;r[c+1]=v` (saves ~2 bytes)
4. `v*(c<m.get(v,-1))` instead of `v and c<m.get(v,-1)` (saves ~1 byte)
5. Single dict `D` or per-row dict `m` instead of separate M,R dicts
6. `D.get(v,(i,c))` to handle first-occurrence without separate if-check

## Remaining Challenge
Target: under 100 bytes (current: 156 bytes). Need fundamentally different approach or Python trick.
