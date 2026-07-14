# Task 003 Insights

## Generator logic
- Input: 6×3 grid with blue (1) pixels showing first 6 rows of a periodic pattern
- Output: 9×3 grid extending pattern to 9 rows with red (2) pixels
- Pattern repeats every `steps` rows (2 or 3), flipping horizontally when `flip=1`
- Period P: 2 (steps=2, no flip), 3 (steps=3), or 4 (steps=2, flip)

## Key insight
- For period 2, using r%4 accidentally works because g[2]=g[0] and g[3]=g[1]
- So P is always: 3 if g[0]==g[3] else 4
- `4-(g[0]==g[3])` → 3 or 4

## Byte trends
- v1: 93b — period detection with list [2,4,3]
- v2: 83b — `c*2` instead of `2*(c>0)`, shorter period detection
- v3: 65b — concatenation: g+EXT instead of g[r%P]
- v4: 65b — r%(4-(g[0]==g[3])) approach
- v5: 61b — g+g[2*(g[0]!=g[3]):][:3] — current best
- v6: 62b — tiling (g[:P]*3)[:9]
- v7: 63b — eval/str/replace approach (worse)

## Effective patterns
- Concatenation beats r%P indexing (saves ~4 bytes)
- `2*(g[0]!=g[3])` gives 0 or 2 for slice start
- `g[start:][:3]` takes 3 rows from start position
- `c*2` is optimal cell conversion (3 chars)

## Bottleneck
- `[[c*2for c in r]for r in ` = 25 chars overhead
- Period detection `g[0]==g[3]` = 12 chars, needed in extension selection
- Extension selection `g[2*(g[0]!=g[3]):][:3]` = 22 chars
- Total expression: 25 + 2 + 22 + 1 = 50 chars, + `p=lambda g:` (11) = 61

## Failed attempts
- `eval(str(...).replace('1','2'))` — longer (63b)
- `g[:4-(g[0]==g[3])]*3)[:9]` tiling — longer (62b)
- Single period for all cases — fails (period 4 needs different extension)
- Always using g[2:5] — fails for period 3
- Arithmetic P: `4-(g[0]==g[3])` — correct but same length as slice trick
