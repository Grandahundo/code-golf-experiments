# Task 001 — Insights

## Transformation (from gen.py)
Classic ARC **self-fractal**. Input `g` is s×s (s=3, single color). Output is s²×s²:
`out[R][C] = g[R//s][C//s] and g[R%s][C%s]` — block (R//s,C//s) holds a copy of `g`
only where that block-cell is nonzero; else zeros. Empty = 0 (common.grid default).

## Key golf insight
Since C//s ranges over block-cols and C%s over inner-cols, the output row for
block-row `a` and inner-row `b` is exactly a flat double comprehension:
`[x and y for x in a for y in b]`. Iterating `for a in g for b in g` reproduces
R = a*s+b. This drops `len(g)` entirely — no size variable needed.

- `x and y` returns the color only when both cells nonzero (0 otherwise). Must NOT
  use `x*y` (would give color², fails exact `==` equality check in _verify_impl).
- Verification uses plain `got == expected` (not numpy), but bools/ints compare
  equal element-wise anyway.

## Byte trend
- v1 (114b): explicit `def`, len(g), range(s*s) nested comprehension.
- v2 (66b): fractal-as-double-comprehension lambda — dropped len(g).
- v3 (65b): removed trailing newline.
- v4 (61b): `x and y` → `x&y`. Valid because every nonzero cell shares ONE color C,
  so C&C=C, C&0=0. Saves 4 bytes. (`and`=7, `&`=1.)

## Failed / worse variants
- v5 (71b): index form `g[i//3][j//3]&g[i%3][j%3]` over range(9) — divmod indexing
  costs far more than iterating rows directly.
- v6 (64b, FAIL): `c*(d>0)` mask — both worse bytes AND I mis-ordered the vars.
  `*` mask is 8 chars vs `&` 3 anyway.

## Exhaustive search for sub-61 (all pure-Python)
Tested computationally against the real 6 cases:
- ALL comprehension orderings/operators (search4, 163 forms): min passing = 61 (`&` only).
- Every 1-, 2-, 3-char DELETION of the 61 solution (mutate.py): 0 pass. So 60/59/58
  are NOT reachable by trimming; and no 2→1 char substitution exists either.
- tile+zip (85), sum-flatten (70), broadcast-zip (85), chain (101), string+convert (163),
  flat+reshape (101): all >61.
=> 61 is provably the pure-Python floor for the value-iterating fractal.
   Body must be 47 for a 58 (prefix `p=lambda g:`=11 fixed); comprehension body min is 50.

## numpy reaches 54 (but BANNED by rules)
`from numpy import*` + `p=lambda g:kron(g,sign(g)).tolist()` = 54 chars, PASSES all 6.
kron(g,sign(g))[3a+b][3cc+c] = g[a][cc]*bool(g[b][c]) = fractal. .tolist() needed so
`got==expected` works (raw ndarray==list raises). numpy is installed here but rule #5
forbids it. So sub-61 exists ONLY via numpy under current knowledge.
=> The human's 58 is likely numpy-based (numpy optimum is 54<58), OR a pure-Python
   trick not in my search space. Awaiting user clarification.

## Why 50 is not reachable (pure stdlib)
The transform is a Kronecker-& of g with itself. Irreducible pieces:
- `p=lambda g:` = 11b (minimal named callable).
- `&` = 1b (shortest binary op; needs single-color invariant).
- Two nested cartesian products = the Kronecker structure. Cannot merge/shorten
  without itertools.product (import cost) or numpy.kron (banned).
Floor for this algorithm ≈ 61b. Sub-60 would need numpy's kron/outer.

## Final (61b) — BEST
`p=lambda g:[[x&y for x in a for y in b]for a in g for b in g]`
