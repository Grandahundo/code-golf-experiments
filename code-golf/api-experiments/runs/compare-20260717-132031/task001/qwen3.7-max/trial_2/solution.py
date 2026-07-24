def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    out_rows = rows * rows
    out_cols = cols * cols
    output = [[0] * out_cols for _ in range(out_rows)]
    for R in range(rows):
        for C in range(cols):
            if grid[R][C] != 0:
                for r in range(rows):
                    for c in range(cols):
                        output[R * rows + r][C * cols + c] = grid[r][c]
    return output
