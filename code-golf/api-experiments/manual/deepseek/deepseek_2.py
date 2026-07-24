def p(grid):
    n = len(grid)
    if n == 0:
        return []
    m = len(grid[0])

    out_rows = n * n
    out_cols = m * m
    out = [[0] * out_cols for _ in range(out_rows)]

    for i in range(n):
        for j in range(m):
            if grid[i][j] != 0:
                for r in range(n):
                    for c in range(m):
                        out[i * n + r][j * m + c] = grid[r][c]

    return out