def p(grid):
    # Determine the separator value S (the value that fills entire rows and columns)
    S = None
    for row in grid:
        if all(c == row[0] and c != 0 for c in row):
            S = row[0]
            break
    if S is None:
        # fallback: should not happen in valid tasks
        return grid

    H = len(grid)
    W = len(grid[0])

    # Find separator rows (full rows of S)
    sep_rows = [i for i in range(H) if all(grid[i][j] == S for j in range(W))]
    # Find separator columns (full columns of S)
    sep_cols = [j for j in range(W) if all(grid[i][j] == S for i in range(H))]

    num_cell_rows = len(sep_rows) - 1
    num_cell_cols = len(sep_cols) - 1

    if num_cell_rows <= 0 or num_cell_cols <= 0:
        # No cells to operate on
        return [row[:] for row in grid]

    # Extract the cell grid (each cell is a 2x2 block between separators)
    cell_grid = [[0] * num_cell_cols for _ in range(num_cell_rows)]
    for i in range(num_cell_rows):
        r = sep_rows[i] + 1  # first row of the cell block
        for j in range(num_cell_cols):
            c = sep_cols[j] + 1  # first column of the cell block
            cell_grid[i][j] = grid[r][c]  # all four pixels are the same

    # Work on a copy where we will write filled values
    filled = [row[:] for row in cell_grid]
    colors = set(val for row in cell_grid for val in row if val != 0)

    # For each color, do horizontal and vertical gap filling based on the original positions
    for C in sorted(colors):  # deterministic order
        # Horizontal fill
        for i in range(num_cell_rows):
            cols = [j for j in range(num_cell_cols) if cell_grid[i][j] == C]
            if len(cols) >= 2:
                min_c, max_c = min(cols), max(cols)
                for j in range(min_c, max_c + 1):
                    if filled[i][j] == 0:
                        filled[i][j] = C
        # Vertical fill
        for j in range(num_cell_cols):
            rows = [i for i in range(num_cell_rows) if cell_grid[i][j] == C]
            if len(rows) >= 2:
                min_r, max_r = min(rows), max(rows)
                for i in range(min_r, max_r + 1):
                    if filled[i][j] == 0:
                        filled[i][j] = C

    # Build output grid
    output = [row[:] for row in grid]  # copy of input
    for i in range(num_cell_rows):
        r_start = sep_rows[i] + 1
        r_end = sep_rows[i+1] - 1
        for j in range(num_cell_cols):
            c_start = sep_cols[j] + 1
            c_end = sep_cols[j+1] - 1
            color = filled[i][j]
            for r in range(r_start, r_end + 1):
                for c in range(c_start, c_end + 1):
                    output[r][c] = color

    return output
