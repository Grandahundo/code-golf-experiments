def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    
    from collections import defaultdict
    color_cells = defaultdict(list)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                color_cells[grid[r][c]].append((r, c))
    
    if not color_cells:
        return [row[:] for row in grid]
    
    template_color = max(color_cells, key=lambda k: len(color_cells[k]))
    template_cells = color_cells[template_color]
    
    min_r = min(r for r, c in template_cells)
    max_r = max(r for r, c in template_cells)
    min_c = min(c for r, c in template_cells)
    max_c = max(c for r, c in template_cells)
    template_h = max_r - min_r + 1
    template_w = max_c - min_c + 1
    tc_r = (min_r + max_r) / 2.0
    tc_c = (min_c + max_c) / 2.0
    
    template_shape = [(r - min_r, c - min_c) for r, c in template_cells]
    
    output = [[0] * cols for _ in range(rows)]
    
    for r, c in template_cells:
        output[r][c] = template_color
    
    step_r = template_h + 1
    step_c = template_w + 1
    
    for color, cells in color_cells.items():
        if color == template_color:
            continue
        
        s_min_r = min(r for r, c in cells)
        s_max_r = max(r for r, c in cells)
        s_min_c = min(c for r, c in cells)
        s_max_c = max(c for r, c in cells)
        sc_r = (s_min_r + s_max_r) / 2.0
        sc_c = (s_min_c + s_max_c) / 2.0
        
        dr = sc_r - tc_r
        dc = sc_c - tc_c
        
        abs_dr = abs(dr)
        abs_dc = abs(dc)
        
        if abs_dr < 0.01 and abs_dc < 0.01:
            continue
        
        if abs_dr > 0.01 and abs_dc > 0.01 and min(abs_dr, abs_dc) / max(abs_dr, abs_dc) > 0.5:
            sd_r = step_r if dr > 0 else -step_r
            sd_c = step_c if dc > 0 else -step_c
        else:
            if abs_dr >= abs_dc:
                sd_r = step_r if dr > 0 else -step_r
                sd_c = 0
            else:
                sd_r = 0
                sd_c = step_c if dc > 0 else -step_c
        
        n = 1
        while True:
            ct_r = tc_r + n * sd_r
            ct_c = tc_c + n * sd_c
            
            tt = int(round(ct_r - (template_h - 1) / 2.0))
            tl = int(round(ct_c - (template_w - 1) / 2.0))
            
            if tt >= rows or tl >= cols or tt + template_h <= 0 or tl + template_w <= 0:
                break
            
            for sr, sc in template_shape:
                r = tt + sr
                c = tl + sc
                if 0 <= r < rows and 0 <= c < cols:
                    output[r][c] = color
            
            n += 1
    
    return output
