def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    mapping = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                mapping[(r + c) % 3] = grid[r][c]
    
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append(mapping[(r + c) % 3])
        output.append(row)
    
    return output
