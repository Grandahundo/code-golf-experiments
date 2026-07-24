def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    
    # Collect positions of 2s and 8s
    cells2 = []
    cells8 = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                cells2.append((r, c))
            elif grid[r][c] == 8:
                cells8.append((r, c))
    
    # If one of the objects is missing, return a copy of the grid
    if not cells2 or not cells8:
        return [row[:] for row in grid]
    
    # Bounding boxes
    min_r2 = min(r for r, c in cells2)
    max_r2 = max(r for r, c in cells2)
    min_c2 = min(c for r, c in cells2)
    max_c2 = max(c for r, c in cells2)
    
    min_r8 = min(r for r, c in cells8)
    max_r8 = max(r for r, c in cells8)
    min_c8 = min(c for r, c in cells8)
    max_c8 = max(c for r, c in cells8)
    
    # Compute vertical shift dr
    if max_r2 < min_r8:
        dr = min_r8 - max_r2 - 1
    elif max_r8 < min_r2:
        dr = -(min_r2 - max_r8 - 1)
    else:
        dr = 0
        
    # Compute horizontal shift dc
    if max_c2 < min_c8:
        dc = min_c8 - max_c2 - 1
    elif max_c8 < min_c2:
        dc = -(min_c2 - max_c8 - 1)
    else:
        dc = 0
        
    # Create output grid
    out = [[0] * cols for _ in range(rows)]
    
    # Place stationary 8s
    for r, c in cells8:
        out[r][c] = 8
        
    # Place shifted 2s
    for r, c in cells2:
        nr = r + dr
        nc = c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            out[nr][nc] = 2
            
    return out
