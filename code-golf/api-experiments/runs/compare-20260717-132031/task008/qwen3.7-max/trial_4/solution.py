def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    shapes = {}
    for r in range(rows):
        for c in range(cols):
            val = grid[r][c]
            if val != 0:
                if val not in shapes:
                    shapes[val] = {'min_r': r, 'max_r': r, 'min_c': c, 'max_c': c, 'cells': []}
                else:
                    shapes[val]['min_r'] = min(shapes[val]['min_r'], r)
                    shapes[val]['max_r'] = max(shapes[val]['max_r'], r)
                    shapes[val]['min_c'] = min(shapes[val]['min_c'], c)
                    shapes[val]['max_c'] = max(shapes[val]['max_c'], c)
                shapes[val]['cells'].append((r, c))
    
    colors = sorted(shapes.keys())
    move_color = colors[0]
    fixed_color = colors[1]
    
    sm = shapes[move_color]
    sf = shapes[fixed_color]
    
    if sm['min_r'] > sf['max_r']:
        v_gap = sm['min_r'] - sf['max_r'] - 1
        v_dir = -1
    elif sf['min_r'] > sm['max_r']:
        v_gap = sf['min_r'] - sm['max_r'] - 1
        v_dir = 1
    else:
        v_gap = -1
        v_dir = 0
    
    if sm['min_c'] > sf['max_c']:
        h_gap = sm['min_c'] - sf['max_c'] - 1
        h_dir = -1
    elif sf['min_c'] > sm['max_c']:
        h_gap = sf['min_c'] - sm['max_c'] - 1
        h_dir = 1
    else:
        h_gap = -1
        h_dir = 0
    
    dr, dc = 0, 0
    if v_gap >= 0 and h_gap < 0:
        dr = v_dir * v_gap
    elif h_gap >= 0 and v_gap < 0:
        dc = h_dir * h_gap
    elif v_gap >= 0 and h_gap >= 0:
        if v_gap <= h_gap:
            dr = v_dir * v_gap
        else:
            dc = h_dir * h_gap
    
    output = [[0] * cols for _ in range(rows)]
    
    for r, c in sf['cells']:
        output[r][c] = fixed_color
    
    for r, c in sm['cells']:
        output[r + dr][c + dc] = move_color
    
    return output
