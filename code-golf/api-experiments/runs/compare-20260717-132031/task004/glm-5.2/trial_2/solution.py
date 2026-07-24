def p(grid):
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    
    visited = [[False] * cols for _ in range(rows)]
    output = [[0] * cols for _ in range(rows)]
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                component = []
                queue = [(r, c)]
                visited[r][c] = True
                while queue:
                    cr, cc = queue.pop(0)
                    component.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                
                max_r = max(cell[0] for cell in component)
                max_c = max(cell[1] for cell in component)
                
                for cr, cc in component:
                    if cr < max_r and cc < max_c:
                        output[cr][cc + 1] = color
                    else:
                        output[cr][cc] = color
    
    return output
