def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find columns with 5s and their topmost row
    col_info = []
    for c in range(cols):
        for r in range(rows):
            if grid[r][c] == 5:
                col_info.append((r, c))
                break
    
    # Sort by topmost row of 5
    col_info.sort()
    
    # Create label mapping: column -> label
    label_map = {}
    for i, (r, c) in enumerate(col_info):
        label_map[c] = i + 1
    
    # Create output grid replacing 5s with labels
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if grid[r][c] == 5:
                row.append(label_map[c])
            else:
                row.append(grid[r][c])
        output.append(row)
    
    return output
