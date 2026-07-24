def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find grid line rows (entire row is the same non-zero value)
    grid_row_indices = []
    for r in range(rows):
        val = grid[r][0]
        if val != 0 and all(grid[r][c] == val for c in range(cols)):
            grid_row_indices.append(r)
    
    # Find grid line cols (entire col is the same non-zero value)
    grid_col_indices = []
    for c in range(cols):
        val = grid[0][c]
        if val != 0 and all(grid[r][c] == val for r in range(rows)):
            grid_col_indices.append(c)
    
    # Compute cell row ranges (regions between grid lines)
    cell_row_ranges = []
    prev = -1
    for idx in grid_row_indices:
        if idx - prev > 1:
            cell_row_ranges.append((prev + 1, idx - 1))
        prev = idx
    if rows - 1 - prev > 0:
        cell_row_ranges.append((prev + 1, rows - 1))
    
    # Compute cell col ranges
    cell_col_ranges = []
    prev = -1
    for idx in grid_col_indices:
        if idx - prev > 1:
            cell_col_ranges.append((prev + 1, idx - 1))
        prev = idx
    if cols - 1 - prev > 0:
        cell_col_ranges.append((prev + 1, cols - 1))
    
    num_cell_rows = len(cell_row_ranges)
    num_cell_cols = len(cell_col_ranges)
    
    # Extract cell values (top-left pixel of each cell)
    cells = [[0] * num_cell_cols for _ in range(num_cell_rows)]
    for i in range(num_cell_rows):
        for j in range(num_cell_cols):
            r = cell_row_ranges[i][0]
            c = cell_col_ranges[j][0]
            cells[i][j] = grid[r][c]
    
    # Step 1: Vertical fill - for each column, fill between matching non-zero values
    for j in range(num_cell_cols):
        value_positions = {}
        for i in range(num_cell_rows):
            v = cells[i][j]
            if v != 0:
                if v not in value_positions:
                    value_positions[v] = []
                value_positions[v].append(i)
        for v, positions in value_positions.items():
            min_pos = min(positions)
            max_pos = max(positions)
            for i in range(min_pos, max_pos + 1):
                cells[i][j] = v
    
    # Step 2: Horizontal fill - for each row, fill between matching non-zero values
    for i in range(num_cell_rows):
        value_positions = {}
        for j in range(num_cell_cols):
            v = cells[i][j]
            if v != 0:
                if v not in value_positions:
                    value_positions[v] = []
                value_positions[v].append(j)
        for v, positions in value_positions.items():
            min_pos = min(positions)
            max_pos = max(positions)
            for j in range(min_pos, max_pos + 1):
                cells[i][j] = v
    
    # Write cells back to grid
    result = [row[:] for row in grid]
    for i in range(num_cell_rows):
        for j in range(num_cell_cols):
            v = cells[i][j]
            for r in range(cell_row_ranges[i][0], cell_row_ranges[i][1] + 1):
                for c in range(cell_col_ranges[j][0], cell_col_ranges[j][1] + 1):
                    result[r][c] = v
    
    return result
