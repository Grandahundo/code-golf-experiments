```python
def p(grid):
    H = len(grid)
    W = len(grid[0]) if H else 0

    # Find the grid-line color (full horizontal/vertical lines).
    C = None
    for r in range(H):
        v = grid[r][0]
        if v != 0 and all(grid[r][c] == v for c in range(W)):
            C = v
            break
    if C is None:
        return [row[:] for row in grid]

    line_rows = [r for r in range(H) if all(grid[r][c] == C for c in range(W))]
    line_cols = [c for c in range(W) if all(grid[r][c] == C for r in range(H))]

    def bands(n, line_set):
        line_set = set(line_set)
        out = []
        i = 0
        while i < n:
            if i in line_set:
                i += 1
                continue
            s = i
            while i < n and i not in line_set:
                i += 1
            out.append((s, i - 1))
        return out

    rb = bands(H, line_rows)
    cb = bands(W, line_cols)
    R = len(rb)
    Col = len(cb)

    cells = [[0] * Col for _ in range(R)]
    for i, (rs, re) in enumerate(rb):
        for j, (cs, ce) in enumerate(cb):
            seen = set()
            for r in range(rs, re + 1):
                for c in range(cs, ce + 1):
                    v = grid[r][c]
                    if v != 0 and v != C:
                        seen.add(v)
            cells[i][j] = min(seen) if seen else 0

    orig = [row[:] for row in cells]
    colors = sorted({orig[i][j] for i in range(R) for j in range(Col)
                     if orig[i][j] not in (0, C)})

    for color in colors:
        for i in range(R):
            js = [j for j in range(Col) if orig[i][j] == color]
            if len(js) >= 2:
                for j in range(min(js), max(js) + 1):
                    if cells[i][j] in (0, color):
                        cells[i][j] = color
        for j in range(Col):
            is_ = [i for i in range(R) if orig[i][j] == color]
            if len(is_) >= 2:
                for i in range(min(is_), max(is_) + 1):
                    if cells[i][j] in (0, color):
                        cells[i][j] = color

    out = [row[:] for row in grid]
    for i, (rs, re) in enumerate(rb):
        for j, (cs, ce) in enumerate(cb):
            v = cells[i][j]
            if v not in (0, C):
                for r in range(rs, re + 1):
                    for c in range(cs, ce + 1):
                        out[r][c] = v
    return out
```