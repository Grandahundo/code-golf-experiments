# Task 001 Insights (agentB analysis)

## Transformation (from gen.py)
Fractal self-tiling / self-Kronecker with `&`.
`output[a][b] = g[a//3][b//3] & g[a%3][b%3]`  (all grids are 3x3).
Both operands in {0,c}: c&c=c, c&0=0, 0&*=0. `&` (3 chars) is the shortest correct combine.
(`v*x`->c^2 wrong; `|`,`^` wrong; `and`,`min`,`x*(v>0)` longer.)

## BEST VERIFIED: 61 bytes (v3.py / agentA_1.py)
  p=lambda g:[[v&x for v in R for x in r]for R in g for r in g]
  Passes 6/6. No trailing newline. wc -c = 61.

## Why 61 is OPTIMAL (proof of a lower bound for this structure)
- Output O[a][b]=g[i][j]&g[p][q] with a=(i,p), b=(j,q). This MIXES a's row-index
  with b's col-index (g[i][j] uses i from a, j from b). So O is NOT separable as
  f(a)&f(b) => O is NOT any flat self-outer-product. The tempting 55-byte
  `[[a&b for b in sum(g,[])]for a in sum(g,[])]` FAILS (verified) for this reason.
- A correct kron needs 4 loops: 2 for rows (R,r pairs = product g x g) and
  2 for cols (v,x pairs = product row x row). No import-free way to get a
  cartesian product cheaper than `for X in Y` twice.
- All 4-loop orderings verified = 61. All flatten/sum/zip/list-mult rewrites are LONGER
  (68-88 bytes). lambda prefix `p=lambda g:` (11) is minimal; `def` version is 16+.
- Body must be <44 for total <55, but 4 required loop-clauses (~10 each) + `v&x` + brackets
  cannot fit in 44. => <55 is impossible for this task.

## Searches run (all local, workdir/search*.py): none beat 61.
