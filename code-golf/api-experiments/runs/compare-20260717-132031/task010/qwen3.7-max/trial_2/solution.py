def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find columns with 5s and the row of their first occurrence
    col_first = {}
    for c in range(cols):
        for r in range(rows):
            if grid[r][c] == 5:
                col_first[c] = r
                break
    
    # Sort columns by first row of 5, then by column index as tiebreaker
    sorted_cols = sorted(col_first.keys(), key=lambda c: (col_first[c], c))
    
    # Assign labels 1, 2, 3, ...
    labels = {}
    for i, c in enumerate(sorted_cols):
        labels[c] = i + 1
    
    # Build output grid: replace 5 with label, keep everything else
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if grid[r][c] == 5:
                row.append(labels[c])
            else:
                row.append(grid[r][c])
        output.append(row)
    
    return output
