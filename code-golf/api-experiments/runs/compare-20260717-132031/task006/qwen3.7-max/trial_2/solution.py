def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find the separator column (all values are 5)
    sep_col = None
    for j in range(cols):
        if all(grid[i][j] == 5 for i in range(rows)):
            sep_col = j
            break
    
    out_cols = sep_col
    
    output = []
    for i in range(rows):
        row = []
        for j in range(out_cols):
            left_val = grid[i][j]
            right_val = grid[i][sep_col + 1 + j]
            if left_val == 1 and right_val == 1:
                row.append(2)
            else:
                row.append(0)
        output.append(row)
    
    return output
