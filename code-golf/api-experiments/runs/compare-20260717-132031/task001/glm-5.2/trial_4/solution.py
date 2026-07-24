def p(grid):
    n = len(grid)
    m = len(grid[0]) if n else 0
    out = [[0] * (n * m) for _ in range(n * m)]
    for i in range(n):
        for j in range(m):
            if grid[i][j] != 0:
                for k in range(n):
                    for l in range(m):
                        out[i * n + k][j * m + l] = grid[k][l]
    return out
