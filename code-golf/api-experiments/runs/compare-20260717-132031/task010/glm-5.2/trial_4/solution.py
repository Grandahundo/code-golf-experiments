def p(grid):
    if not grid:
        return []
    rows = len(grid)
    cols = len(grid[0])
    
    # Find the topmost (first) row containing a 5 for each column
    col_topmost = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 5:
                if c not in col_topmost:
                    col_topmost[c] = r
    
    # Sort columns by the row of their topmost 5 (tiebreak by column index)
    sorted_cols = sorted(col_topmost.keys(), key=lambda c: (col_topmost[c], c))
    
    # Assign colors 1, 2, 3, ... in order of first appearance from top
    col_to_color = {}
    for i, c in enumerate(sorted_cols):
        col_to_color[c] = i + 1
    
    # Build output: replace each 5 with its column's assigned color
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if grid[r][c] == 5:
                row.append(col_to_color[c])
            else:
                row.append(grid[r][c])
        output.append(row)
    
    return output
