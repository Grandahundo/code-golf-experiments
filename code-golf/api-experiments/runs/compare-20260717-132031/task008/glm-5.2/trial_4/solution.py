def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    
    red_cells = []
    azure_cells = []
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v == 2:
                red_cells.append((r, c))
            elif v == 8:
                azure_cells.append((r, c))
    
    if not red_cells or not azure_cells:
        return [row[:] for row in grid]
    
    red_rows = [r for r, _ in red_cells]
    red_cols = [c for _, c in red_cells]
    az_rows = [r for r, _ in azure_cells]
    az_cols = [c for _, c in azure_cells]
    
    red_rmin, red_rmax = min(red_rows), max(red_rows)
    red_cmin, red_cmax = min(red_cols), max(red_cols)
    az_rmin, az_rmax = min(az_rows), max(az_rows)
    az_cmin, az_cmax = min(az_cols), max(az_cols)
    
    col_overlap = red_cmin <= az_cmax and az_cmin <= red_cmax
    row_overlap = red_rmin <= az_rmax and az_rmin <= red_rmax
    
    dr, dc = 0, 0
    if col_overlap and not row_overlap:
        if red_rmax < az_rmin:
            dr = az_rmin - 1 - red_rmax
        else:
            dr = az_rmax + 1 - red_rmin
    elif row_overlap and not col_overlap:
        if red_cmax < az_cmin:
            dc = az_cmin - 1 - red_cmax
        else:
            dc = az_cmax + 1 - red_cmin
    else:
        # Fallback: move along the axis with the larger separation
        v_sep = max(az_rmin - red_rmax - 1, red_rmin - az_rmax - 1, 0)
        h_sep = max(az_cmin - red_cmax - 1, red_cmin - az_cmax - 1, 0)
        if v_sep >= h_sep:
            if red_rmax < az_rmin:
                dr = az_rmin - 1 - red_rmax
            else:
                dr = az_rmax + 1 - red_rmin
        else:
            if red_cmax < az_cmin:
                dc = az_cmin - 1 - red_cmax
            else:
                dc = az_cmax + 1 - red_cmin
    
    output = [[0] * cols for _ in range(rows)]
    for r, c in azure_cells:
        output[r][c] = 8
    for r, c in red_cells:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            output[nr][nc] = 2
    
    return output
