def p(grid):
    r = len(grid)
    if r == 0:
        return []
    c = len(grid[0])

    out = [[0] * (c * c) for _ in range(r * r)]

    for i in range(r):
        for j in range(c):
            if grid[i][j] != 0:
                for di in range(r):
                    for dj in range(c):
                        out[i * r + di][j * c + dj] = grid[di][dj]

    return out