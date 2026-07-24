# Task 004 — Insights

## Transformation (from gen.py)
Parallelogram outlines (top+bottom horizontal, left+right diagonals slope 1 down-right).
Per component: top edge & diagonals shift right +1; bottom row stays; right-diagonal
bottom pixel (clamp, at col+wide-1) stays.

## Key facts
- Shapes stack vertically, separated by ≥1 blank row → segment by blank rows.
- Every row of a shape is non-empty (outline has diagonal pixels each row).
- **Gather formula (source-based, single shift eval):**
  `out[r][c] = R[c-shift]` where `shift = 1` iff the source pixel at (r,c-1) shifts.
- shift(r,c-1) = row-below-nonblank AND cell directly below source is empty:
  `any(n) and n[c-1] < 1`   (n = row r+1)
- **`b[r+2]` / `any(m)` NOT needed!** Only top-left corner and clamp have a colored
  cell directly below. Both produce the correct COLOR value when treated as "stay"
  (their same-color neighbors fill the slot), so distinguishing them is unnecessary.
- Short-circuit `and` is required so `n[c-1]` isn't evaluated when n=[] (last row pad).
  `*` instead of `and` → IndexError on empty pad row.

## Byte trend
400 → 229 → 188 → 145(single-shift gather) → 135(R[c-shift]) → 122(lambda+walrus)
→ 116(zip rows) → 90(drop m).

## FINAL: v15 = 90 bytes
p=lambda g:[[R[c-(any(n)and n[c-1]<1)]for c in range(len(R))]for R,n in zip(g,g[1:]+[[]])]

## Failed ideas
- below-LEFT g[r+1][c-1] as the stay test in scatter (v8): top edge above left-diagonal
  wrongly flagged as stay.
- row-level shift + clamp patch (v6): m+1 index out of range when maxcol == W-1.
- `*` instead of `and`: loses short-circuit, IndexError on [] pad.
