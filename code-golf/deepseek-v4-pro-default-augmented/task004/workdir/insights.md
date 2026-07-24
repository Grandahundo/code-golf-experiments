# Task 004 Insights

## Best working solution
- v18.py: 194 bytes (all tests pass)
- v2.py: 197 bytes (all tests pass)

## Transformation logic (derived from gen.py)
Input: grid with parallelogram outlines (0-9 color values)
Output: grid where parallelograms are shifted right by 1, except:
  - Bottom row pixels stay in place
  - Rightmost pixel of second-to-last row stays (clamped by bottom-right corner)

## Core per-pixel rule
For pixel at (r,c) with value v:
- a = color appears in row above (r>0 and v in g[r-1])
- b = color appears in row below (r<H-1 and v in g[r+1])
- d = pixel directly below is different (g[r+1][c] != v)
- shift = not a or (b and d)

Stay conditions: bottom row (no color below) OR pixel below matches AND pixel to right differs
Shift conditions: top row (no color above) OR (not bottom AND pixel below differs)

## Attempted approaches
1. Per-pixel with a,b variables: v2 (197 bytes) - shortest working
2. Lambda with exec: v5 (220 bytes)
3. Recursive: v6 (248 bytes)
4. Two-pass shift-then-fix: v7 (234 bytes)
5. Bottom-up set tracking: v8 (257 bytes, buggy: mid-row set add breaks bottom detection)
6. Copy + right-to-left: v11 (215 bytes)
7. Extreme one-liner def: v14 (210 bytes)
8. Parameter extraction + regeneration: v15 (321 bytes)
9. Padded grid: v16 (224 bytes)
10. Micro-optimized v2: v18 (194 bytes)

## Key challenge
Target is <100 bytes but all approaches are 194+ bytes. The per-pixel logic
is irreducible (needs 3 checks: color above, color below, pixel directly below)
and grid iteration overhead is significant. A fundamentally different algorithm
or Python trick must exist that I haven't discovered.

## Failed shortcuts
- "shift if g[r+1][c]!=v" fails for top-left pixel (has pixel below matching, should shift)
- "shift if column bottommost" fails because bottom-of-column ≠ bottom-of-component
- Simple row-shift without per-pixel checks fails for right-diagonal clamping
- Using `&` without parens: precedence issue (`!=` has lower precedence than `&`)
- `g[r+1][c]-v` leaks int through `or`, causing wrong column indices
