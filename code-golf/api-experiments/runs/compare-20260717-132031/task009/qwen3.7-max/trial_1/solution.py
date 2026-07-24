def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    num_cell_rows = (rows + 1) // 3
    num_cell_cols = (cols + 1) // 3
    
    # Extract original cell values
    cell = [[0] * num_cell_cols for _ in range(num_cell_rows)]
    for r in range(num_cell_rows):
        for c in range(num_cell_cols):
            cell[r][c] = grid[3 * r][3 * c]
    
    # Output cells, initialized to original values
    out = [row[:] for row in cell]
    
    # Row fills: for each row, fill between min and max column of each value
    for r in range(num_cell_rows):
        values = {}
        for c in range(num_cell_cols):
            v = cell[r][c]
            if v > 0:
                if v not in values:
                    values[v] = []
                values[v].append(c)
        for v, cs in values.items():
            if len(cs) >= 2:
                c_min, c_max = min(cs), max(cs)
                for c in range(c_min, c_max + 1):
                    out[r][c] = v
    
    # Column fills: for each column, fill between min and max row of each value
    for c in range(num_cell_cols):
        values = {}
        for r in range(num_cell_rows):
            v = cell[r][c]
            if v > 0:
                if v not in values:
                    values[v] = []
                values[v].append(r)
        for v, rs in values.items():
            if len(rs) >= 2:
                r_min, r_max = min(rs), max(rs)
                for r in range(r_min, r_max + 1):
                    out[r][c] = v
    
    # Construct output grid from output cells
    result = [row[:] for row in grid]
    for r in range(num_cell_rows):
        for c in range(num_cell_cols):
            v = out[r][c]
            gr, gc = 3 * r, 3 * c
            result[gr][gc] = v
            result[gr][gc + 1] = v
            result[gr + 1][gc] = v
            result[gr + 1][gc + 1] = v
    
    return result
