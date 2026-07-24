def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    sep_col = cols // 2
    left_cols = sep_col
    right_start = sep_col + 1
    
    output = []
    for i in range(rows):
        row = []
        for j in range(left_cols):
            l = grid[i][j]
            r = grid[i][right_start + j]
            if l == r:
                row.append(l + r)
            else:
                row.append(0)
        output.append(row)
    
    return output
