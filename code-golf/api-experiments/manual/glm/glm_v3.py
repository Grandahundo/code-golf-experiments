def p(grid):
    if not grid or not grid[0]:
        return []
    R = len(grid)
    C = len(grid[0])
    out = [[0] * (C * C) for _ in range(R * R)]
    for i in range(R):
        for j in range(C):
            if grid[i][j] != 0:
                for r in range(R):
                    for c in range(C):
                        out[i * R + r][j * C + c] = grid[r][c]
    return out