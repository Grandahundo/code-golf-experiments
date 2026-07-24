def p(grid):
    H = len(grid)
    W = len(grid[0])
    out_H = 3 * H
    out_W = 3 * W
    out = [[0] * out_W for _ in range(out_H)]
    for i in range(H):
        for j in range(W):
            if grid[i][j] != 0:
                for r in range(H):
                    for c in range(W):
                        out[i * H + r][j * W + c] = grid[r][c]
    return out
