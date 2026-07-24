def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    visited = [[False]*cols for _ in range(rows)]
    objects = []
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                stack = [(r, c)]
                visited[r][c] = True
                cells = []
                while stack:
                    cr, cc = stack.pop()
                    cells.append((cr, cc))
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nr, nc = cr+dr, cc+dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                objects.append((color, cells))
    
    if not objects:
        return [row[:] for row in grid]
    
    template_idx = max(range(len(objects)), key=lambda i: len(objects[i][1]))
    _, template_cells = objects[template_idx]
    
    t_rows = [r for r, c in template_cells]
    t_cols = [c for r, c in template_cells]
    tr_min, tr_max = min(t_rows), max(t_rows)
    tc_min, tc_max = min(t_cols), max(t_cols)
    H = tr_max - tr_min + 1
    W = tc_max - tc_min + 1
    
    mask = [[0]*W for _ in range(H)]
    for r, c in template_cells:
        mask[r - tr_min][c - tc_min] = 1
    
    output = [row[:] for row in grid]
    
    for i, (color, cells) in enumerate(objects):
        if i == template_idx:
            continue
        
        s_rows = [r for r, c in cells]
        s_cols = [c for r, c in cells]
        sr_min, sr_max = min(s_rows), max(s_rows)
        sc_min, sc_max = min(s_cols), max(s_cols)
        
        v_dir = 0
        h_dir = 0
        
        if sr_max < tr_min:
            v_dir = -1
        elif sr_min > tr_max:
            v_dir = 1
        
        if sc_max < tc_min:
            h_dir = -1
        elif sc_min > tc_max:
            h_dir = 1
        
        if v_dir == 0 and h_dir == 0:
            continue
        
        if v_dir == -1:
            first_row = tr_min - (H + 1)
            row_step = -(H + 1)
        elif v_dir == 1:
            first_row = tr_min + (H + 1)
            row_step = (H + 1)
        else:
            first_row = tr_min
            row_step = 0
        
        if h_dir == -1:
            first_col = tc_min - (W + 1)
            col_step = -(W + 1)
        elif h_dir == 1:
            first_col = tc_min + (W + 1)
            col_step = (W + 1)
        else:
            first_col = tc_min
            col_step = 0
        
        sr = first_row
        sc = first_col
        while True:
            if sr >= rows or sr + H - 1 < 0:
                break
            if sc >= cols or sc + W - 1 < 0:
                break
            for dr in range(H):
                for dc in range(W):
                    if mask[dr][dc]:
                        r = sr + dr
                        c = sc + dc
                        if 0 <= r < rows and 0 <= c < cols:
                            output[r][c] = color
            sr += row_step
            sc += col_step
    
    return output
