def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # Find all non-zero values and their (r+c) values
    rc_values = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                rc = r + c
                rc_values[rc] = grid[r][c]
    
    P = len(rc_values)
    
    # Build the sequence
    sequence = [0] * P
    for rc, v in rc_values.items():
        idx = rc % P
        sequence[idx] = v
    
    # Fill the output
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            row.append(sequence[(r + c) % P])
        output.append(row)
    
    return output
