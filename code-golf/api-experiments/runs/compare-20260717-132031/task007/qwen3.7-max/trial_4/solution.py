def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    mapping = {}
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v != 0:
                idx = (r + c) % 3
                mapping[idx] = v
    
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            idx = (r + c) % 3
            row.append(mapping[idx])
        output.append(row)
    
    return output
