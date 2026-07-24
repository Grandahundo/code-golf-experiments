def p(grid):
    # Find the column that acts as a separator (all 5s)
    rows = len(grid)
    cols = len(grid[0])
    sep_col = -1
    for c in range(cols):
        if all(grid[r][c] == 5 for r in range(rows)):
            sep_col = c
            break
    # If no separator column found, assume the middle column is the separator
    if sep_col == -1:
        sep_col = cols // 2

    left_width = sep_col
    right_start = sep_col + 1
    out_rows = rows
    out_cols = left_width
    out = [[0] * out_cols for _ in range(out_rows)]

    for r in range(rows):
        for c in range(left_width):
            if grid[r][c] == 1 and grid[r][right_start + c] == 1:
                out[r][c] = 2
            # else remains 0

    return out
