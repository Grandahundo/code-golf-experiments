def p(grid):
    N = len(grid)
    M = len(grid[0]) if N > 0 else 0
    output = [[0] * (M * M) for _ in range(N * N)]
    for i in range(N):
        for j in range(M):
            if grid[i][j] != 0:
                for bi in range(N):
                    for bj in range(M):
                        output[i * N + bi][j * M + bj] = grid[bi][bj]
    return output
