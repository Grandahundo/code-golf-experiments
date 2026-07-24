def p(grid):
    h = len(grid)
    w = len(grid[0]) if h else 0
    out = [[0] * (w * w) for _ in range(h * h)]
    for i in range(h):
        for j in range(w):
            if grid[i][j] != 0:
                r0 = i * h
                c0 = j * w
                for r in range(h):
                    for c in range(w):
                        out[r0 + r][c0 + c] = grid[r][c]
    return out