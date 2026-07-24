def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find the separator column (all values equal to 5)
    sep_col = -1
    for j in range(cols):
        if all(grid[i][j] == 5 for i in range(rows)):
            sep_col = j
            break
    
    # Left grid columns: 0 to sep_col-1
    # Right grid columns: sep_col+1 to end
    left_cols = list(range(0, sep_col))
    right_cols = list(range(sep_col + 1, cols))
    
    out_cols = len(left_cols)
    
    output = []
    for i in range(rows):
        row = []
        for j in range(out_cols):
            l = grid[i][left_cols[j]]
            r = grid[i][right_cols[j]]
            if l != 0 and r != 0:
                row.append(2)
            else:
                row.append(0)
        output.append(row)
    
    return output
