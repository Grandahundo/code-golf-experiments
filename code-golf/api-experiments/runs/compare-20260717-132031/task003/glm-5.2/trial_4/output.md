```python
def p(grid):
    H = len(grid)
    if H == 0:
        return []
    # Find smallest vertical period P such that grid is a prefix of the
    # infinite repetition of its first P rows.
    P = H
    for cand in range(1, H + 1):
        ok = True
        for i in range(cand, H):
            if grid[i] != grid[i % cand]:
                ok = False
                break
        if ok:
            P = cand
            break
    pattern = grid[:P]
    out_h = H + H // 2
    out = []
    for i in range(out_h):
        row = pattern[i % P]
        out.append([2 if x == 1 else x for x in row])
    return out
```