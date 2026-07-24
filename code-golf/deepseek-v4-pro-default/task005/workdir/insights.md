# Task 005 insights

## KEY: verify.py tests only the fixed `validate()` examples in gen.py (3 train + 1 test). Only these 4 matter.

## Transformation
Input = middle sprite (full 3x3-ish shape, color c0 at (srow,scol)) + one partial "arrow" per direction
at center+4*(dir), showing that direction's color. Directions are 8-neighborhood (dr,dc in {-1,0,1}, not both 0).
Output = middle sprite + full sprite stamped along each active ray at (srow+4k*dr, scol+4k*dc), k=1,2,...

## Reconstruction algorithm (works, all 4 pass)
- Middle box top-left (y,x) = argmax over 3x3 windows of nonzero count. Edges of sprite are NEVER fully
  empty (side-removal and diagonal-removal are mutually exclusive in gen), so bounding box is exactly 3x3
  and argmax lands exactly on (srow,scol). srow,scol in [6,12] so center+/-4 windows are always in-bounds.
- shape = nonzero offsets in that window; color per direction = max value in window at center+4*(dir).
- Stamp shape recolored along each ray; center handled as k=0.

## BEST: workdir/vB1.py = 275 bytes, PASS 4/4  (beats aB_10 278, aA_final 338, v9 410)
Command: python3 verify.py workdir/<file>.py
vB1 = aB_10 with D reordered to -4,4,0 (center (0,0) LAST) so k can use plain R(8) instead of
R(1,8): direction k=0 stamps get overwritten by the final center pass. Saves ~3 bytes.
(A lambda one-expression form was tried = 287 bytes, WORSE; def wins.)

    def p(g):
     R=range;D=-4,4,0
     S=max(([(i+a,j+c)for a in R(3)for c in R(3)if g[i+a][j+c]]for i in R(19)for j in R(19)),key=len)
     o={(Y+k*r,X+k*d):max(g[Y+r][X+d]for Y,X in S)for r in D for d in D for k in R(8)for Y,X in S}
     return[[o.get((i,j),0)for j in R(21)]for i in R(21)]

## (previous best below)
## aB_10.py = 278 bytes, PASS 4/4  (beats aA_final 338, v9 410)
Command: python3 verify.py workdir/<file>.py

## 278-byte approach (aB_10.py)
Store S as ABSOLUTE middle-sprite cell coords (not offsets) -> no separate (y,x) anchor needed.
Scale direction vectors by 4 (D=-4,0,4) so all `4*` factors vanish. Whole output = ONE dict
comprehension keyed by (Y+k*r, X+k*d), value = arrow color = max over window at (Y+r, X+d).
Center r=d=0 gives key (Y,X)=middle for any k, so k in R(1,8) uniformly (no center special-case).
Inactive dirs read color 0 -> harmless. Inner max's `for Y,X in S` shadows harmlessly (own genexpr
scope); the key uses the outer comprehension's Y,X. argmax uses max(...,key=len) over the list of
nonzero-cell coord lists (len = nonzero count, NOT value-sum -> correct).

    def p(g):
     R=range
     D=-4,0,4
     S=max(([(i+a,j+c)for a in R(3)for c in R(3)if g[i+a][j+c]]for i in R(19)for j in R(19)),key=len)
     o={(Y+k*r,X+k*d):max(g[Y+r][X+d]for Y,X in S)for r in D for d in D for k in R(1,8)for Y,X in S}
     return[[o.get((i,j),0)for j in R(21)]for i in R(21)]

Progression: 383->366->356->326->302 (single dict-comp)->294 (D=-4,0,4)->282 (absolute S, drop y,x)
->278 (max key=len).

## Prior: workdir/aA_final.py = 338 bytes, PASS 4/4 (was v9.py 410)
Command: python3 verify.py workdir/<file>.py

## 338-byte approach (dict comprehension, no def P, no o mutation)
- G=range alias; r=range(3); R=-1,0,1.
- (y,x)=argmax of nonzero-count 3x3 window (must use `>0` count, NOT value-sum: a high-color
  arrow with 2 cells can outweigh the middle sprite's sum).
- Single dict comprehension D keyed by (row,col):
  for each dir (u,v) in R x R, walrus w:=max over the 3x3 window at center+4*(u,v) (arrow color);
  `if(w:=...)` filters w>0; k in range(u*u|v*v,8) -> start 0 for center (all k give center, harmless),
  start 1 for rays; inner `for a in r for b in r if g[y+a][x+b]` applies the middle sprite shape mask.
- Output grid = [[D.get((i,j),0)for j in G(21)]for i in G(21)]. Off-grid dict keys are never queried.
- Key golf wins vs v9: dict comp instead of nested def+mutation (-56), inline walrus max (-21),
  `u*u|v*v` for k-start (-6), G=range alias (-16).
