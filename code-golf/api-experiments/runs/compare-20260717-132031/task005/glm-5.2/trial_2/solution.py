def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    visited = [[False]*cols for _ in range(rows)]
    shapes = []
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                stack = [(r, c)]
                cells = []
                visited[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    cells.append((cr, cc))
                    for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                        nr, nc = cr+dr, cc+dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                shapes.append((color, cells))
    
    template_idx = -1
    best_cells = -1
    for i, (color, cells) in enumerate(shapes):
        min_r = min(r for r, c in cells)
        max_r = max(r for r, c in cells)
        min_c = min(c for r, c in cells)
        max_c = max(c for r, c in cells)
        if max_r - min_r == 2 and max_c - min_c == 2:
            if len(cells) > best_cells:
                best_cells = len(cells)
                template_idx = i
    
    if template_idx == -1:
        return [row[:] for row in grid]
    
    t_color, t_cells = shapes[template_idx]
    t_min_r = min(r for r, c in t_cells)
    t_max_r = max(r for r, c in t_cells)
    t_min_c = min(c for r, c in t_cells)
    t_max_c = max(c for r, c in t_cells)
    
    t_pattern = [[0]*3 for _ in range(3)]
    for r, c in t_cells:
        t_pattern[r - t_min_r][c - t_min_c] = 1
    
    output = [row[:] for row in grid]
    for i, (color, cells) in enumerate(shapes):
        if i == template_idx:
            continue
        for r, c in cells:
            output[r][c] = 0
    
    for i, (color, cells) in enumerate(shapes):
        if i == template_idx:
            continue
        
        s_min_r = min(r for r, c in cells)
        s_max_r = max(r for r, c in cells)
        s_min_c = min(c for r, c in cells)
        s_max_c = max(c for r, c in cells)
        
        if s_max_r < t_min_r:
            row_dir = -1
        elif s_min_r > t_max_r:
            row_dir = 1
        else:
            row_dir = 0
        
        if s_max_c < t_min_c:
            col_dir = -1
        elif s_min_c > t_max_c:
            col_dir = 1
        else:
            col_dir = 0
        
        if row_dir == 0 and col_dir == 0:
            continue
        
        k = 1
        while True:
            tile_r = t_min_r + row_dir * 4 * k
            tile_c = t_min_c + col_dir * 4 * k
            
            if tile_r + 2 < 0 or tile_r >= rows or tile_c + 2 < 0 or tile_c >= cols:
                break
            
            for dr in range(3):
                for dc in range(3):
                    if t_pattern[dr][dc]:
                        r = tile_r + dr
                        c = tile_c + dc
                        if 0 <= r < rows and 0 <= c < cols:
                            output[r][c] = color
            
            k += 1
    
    return output
