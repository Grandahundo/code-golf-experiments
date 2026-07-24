def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # Locate all cells of value 2 and 8
    twos = []
    eights = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                twos.append((r, c))
            elif grid[r][c] == 8:
                eights.append((r, c))
    
    # If one of the shapes is missing, return original grid
    if not twos or not eights:
        return [row[:] for row in grid]
    
    # Bounding boxes
    min_r2 = min(r for r, _ in twos)
    max_r2 = max(r for r, _ in twos)
    min_c2 = min(c for _, c in twos)
    max_c2 = max(c for _, c in twos)
    
    min_r8 = min(r for r, _ in eights)
    max_r8 = max(r for r, _ in eights)
    min_c8 = min(c for _, c in eights)
    max_c8 = max(c for _, c in eights)
    
    # Check overlap intervals
    cols_overlap = not (max_c2 < min_c8 or max_c8 < min_c2)
    rows_overlap = not (max_r2 < min_r8 or max_r8 < min_r2)
    
    # Determine movement direction and distance
    if cols_overlap:
        dc = 0
        if max_r2 < min_r8:  # 2 above 8
            dr = min_r8 - max_r2 - 1
        else:                # 2 below 8
            dr = max_r8 - min_r2 + 1
    elif rows_overlap:
        dr = 0
        if max_c2 < min_c8:  # 2 left of 8
            dc = min_c8 - max_c2 - 1
        else:                # 2 right of 8
            dc = max_c8 - min_c2 + 1
    else:
        # No overlap in either axis -> no movement (should not happen in task)
        return [row[:] for row in grid]
    
    # Build output grid
    out = [[0] * cols for _ in range(rows)]
    
    # Place stationary 8 shape
    for r, c in eights:
        out[r][c] = 8
    
    # Place relocated 2 shape
    for r, c in twos:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            out[nr][nc] = 2
    
    return out
