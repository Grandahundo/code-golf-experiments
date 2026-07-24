def p(grid):
    R = len(grid)
    C = len(grid[0]) if R else 0
    out = [[0] * (C * C) for _ in range(R * R)]
    for bi in range(R):
        for bj in range(C):
            if grid[bi][bj] != 0:
                for i in range(R):
                    for j in range(C):
                        out[bi * R + i][bj * C + j] = grid[i][j]
    return out
