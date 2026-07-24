def p(grid):
    # Determine the size of the input grid (assumed square)
    n = len(grid)
    # Output grid is n*n by n*n, initially filled with zeros
    out = [[0] * (n * n) for _ in range(n * n)]
    # For each cell in the input, if non-zero, copy the entire input into the corresponding block
    for i in range(n):
        for j in range(n):
            if grid[i][j] != 0:
                # Block starting at row i*n, column j*n
                for r in range(n):
                    for c in range(n):
                        out[i * n + r][j * n + c] = grid[r][c]
    return out
