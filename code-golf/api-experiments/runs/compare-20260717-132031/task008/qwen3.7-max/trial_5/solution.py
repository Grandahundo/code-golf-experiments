def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    shapes = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                color = grid[r][c]
                if color not in shapes:
                    shapes[color] = []
                shapes[color].append((r, c))
    
    colors = sorted(shapes.keys())
    moving_color = colors[0]
    target_color = colors[1]
    
    moving_cells = shapes[moving_color]
    target_cells = shapes[target_color]
    
    m_top = min(r for r, c in moving_cells)
    m_bottom = max(r for r, c in moving_cells)
    m_left = min(c for r, c in moving_cells)
    m_right = max(c for r, c in moving_cells)
    
    t_top = min(r for r, c in target_cells)
    t_bottom = max(r for r, c in target_cells)
    t_left = min(c for r, c in target_cells)
    t_right = max(c for r, c in target_cells)
    
    v_gap = max(0, max(m_top - t_bottom - 1, t_top - m_bottom - 1))
    h_gap = max(0, max(m_left - t_right - 1, t_left - m_right - 1))
    
    dr, dc = 0, 0
    if v_gap >= h_gap:
        if m_top > t_bottom:
            dr = -v_gap
        else:
            dr = v_gap
    else:
        if m_left > t_right:
            dc = -h_gap
        else:
            dc = h_gap
    
    output = [[0] * cols for _ in range(rows)]
    
    for r, c in target_cells:
        output[r][c] = target_color
    
    for r, c in moving_cells:
        output[r + dr][c + dc] = moving_color
    
    return output
