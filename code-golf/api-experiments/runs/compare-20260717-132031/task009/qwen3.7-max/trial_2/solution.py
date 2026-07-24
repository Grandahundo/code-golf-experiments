def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    num_block_rows = (rows + 1) // 3
    num_block_cols = (cols + 1) // 3
    
    # Extract original cells (2x2 blocks between grid lines)
    cells = [[0] * num_block_cols for _ in range(num_block_rows)]
    for r in range(num_block_rows):
        for c in range(num_block_cols):
            cells[r][c] = grid[3 * r][3 * c]
    
    # Compute fills
    fills = [[0] * num_block_cols for _ in range(num_block_rows)]
    
    # Horizontal fills (based on original cells only)
    for r in range(num_block_rows):
        color_cols = {}
        for c in range(num_block_cols):
            v = cells[r][c]
            if v != 0:
                if v not in color_cols:
                    color_cols[v] = []
                color_cols[v].append(c)
        
        for v, cols_list in color_cols.items():
            if len(cols_list) >= 2:
                min_c = min(cols_list)
                max_c = max(cols_list)
                for c in range(min_c, max_c + 1):
                    if cells[r][c] == 0 and fills[r][c] == 0:
                        fills[r][c] = v
    
    # Vertical fills (based on original cells only)
    for c in range(num_block_cols):
        color_rows = {}
        for r in range(num_block_rows):
            v = cells[r][c]
            if v != 0:
                if v not in color_rows:
                    color_rows[v] = []
                color_rows[v].append(r)
        
        for v, rows_list in color_rows.items():
            if len(rows_list) >= 2:
                min_r = min(rows_list)
                max_r = max(rows_list)
                for r in range(min_r, max_r + 1):
                    if cells[r][c] == 0 and fills[r][c] == 0:
                        fills[r][c] = v
    
    # Apply fills to a copy of the grid
    result = [row[:] for row in grid]
    for r in range(num_block_rows):
        for c in range(num_block_cols):
            if fills[r][c] != 0:
                v = fills[r][c]
                result[3 * r][3 * c] = v
                result[3 * r][3 * c + 1] = v
                result[3 * r + 1][3 * c] = v
                result[3 * r + 1][3 * c + 1] = v
    
    return result
