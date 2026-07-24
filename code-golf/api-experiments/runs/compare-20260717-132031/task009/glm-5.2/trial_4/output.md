```python
from collections import Counter

def p(grid):
    H = len(grid)
    W = len(grid[0]) if H else 0

    # detect separator color from the first uniform row
    sep = None
    for r in range(H):
        if all(grid[r][c] == grid[r][0] for c in range(W)):
            sep = grid[r][0]
            break
    if sep is None:
        return [row[:] for row in grid]

    sep_rows = set(r for r in range(H) if all(grid[r][c] == sep for c in range(W)))
    sep_cols = set(c for c in range(W) if all(grid[r][c] == sep for r in range(H)))

    # group content rows/cols into blocks
    row_blocks = []
    cur = []
    for r in range(H):
        if r in sep_rows:
            if cur:
                row_blocks.append(cur)
                cur = []
        else:
            cur.append(r)
    if cur:
        row_blocks.append(cur)

    col_blocks = []
    cur = []
    for c in range(W):
        if c in sep_cols:
            if cur:
                col_blocks.append(cur)
                cur = []
        else:
            cur.append(c)
    if cur:
        col_blocks.append(cur)

    R = len(row_blocks)
    C = len(col_blocks)

    # build cell grid
    CG = [[0] * C for _ in range(R)]
    for i, rb in enumerate(row_blocks):
        for j, cb in enumerate(col_blocks):
            cnt = Counter()
            for r in rb:
                for c in cb:
                    v = grid[r][c]
                    if v != sep and v != 0:
                        cnt[v] += 1
            CG[i][j] = cnt.most_common(1)[0][0] if cnt else 0

    # apply fills
    CG2 = [row[:] for row in CG]

    # horizontal fills based on original CG
    for i in range(R):
        for c in set(CG[i][j] for j in range(C) if CG[i][j] != 0):
            cols = [j for j in range(C) if CG[i][j] == c]
            if len(cols) >= 2:
                lo, hi = min(cols), max(cols)
                for j in range(lo, hi + 1):
                    CG2[i][j] = c

    # vertical fills based on original CG
    for j in range(C):
        for c in set(CG[i][j] for i in range(R) if CG[i][j] != 0):
            rows = [i for i in range(R) if CG[i][j] == c]
            if len(rows) >= 2:
                lo, hi = min(rows), max(rows)
                for i in range(lo, hi + 1):
                    CG2[i][j] = c

    # expand back to full grid
    out = [[0] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            if r in sep_rows or c in sep_cols:
                out[r][c] = sep
    for i, rb in enumerate(row_blocks):
        for j, cb in enumerate(col_blocks):
            v = CG2[i][j]
            for r in rb:
                for c in cb:
                    out[r][c] = v
    return out
```