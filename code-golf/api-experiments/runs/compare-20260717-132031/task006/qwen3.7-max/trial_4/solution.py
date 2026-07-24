def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find separator column (column with all 5s)
    sep = -1
    for j in range(cols):
        if all(grid[i][j] == 5 for i in range(rows)):
            sep = j
            break
    
    # Left half: columns 0 to sep-1
    # Right half: columns sep+1 to end
    out_cols = min(sep, cols - sep - 1)
    
    output = []
    for i in range(rows):
        row = []
        for j in range(out_cols):
            left_val = grid[i][j]
            right_val = grid[i][sep + 1 + j]
            if left_val == 1 and right_val == 1:
                row.append(2)
            else:
                row.append(0)
        output.append(row)
    
    return output
