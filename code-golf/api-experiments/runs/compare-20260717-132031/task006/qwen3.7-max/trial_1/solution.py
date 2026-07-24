def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find the separator column (column where all values are 5)
    sep_col = -1
    for c in range(cols):
        if all(grid[r][c] == 5 for r in range(rows)):
            sep_col = c
            break
    
    right_start = sep_col + 1
    out_cols = sep_col
    
    output = []
    for r in range(rows):
        row = []
        for c in range(out_cols):
            l_val = grid[r][c]
            r_val = grid[r][right_start + c]
            if l_val == 1 and r_val == 1:
                row.append(2)
            else:
                row.append(0)
        output.append(row)
    
    return output
