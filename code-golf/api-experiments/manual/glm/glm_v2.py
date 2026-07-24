def p(grid):
    H = len(grid)
    W = len(grid[0]) if H else 0
    out = [[0] * (W * W) for _ in range(H * H)]
    for i in range(H):
        for j in range(W):
            if grid[i][j] != 0:
                for a in range(H):
                    for b in range(W):
                        out[i * H + a][j * W + b] = grid[a][b]
    return out