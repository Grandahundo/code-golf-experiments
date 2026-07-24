def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    output = [[0] * cols for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                component = []
                stack = [(r, c)]
                visited[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    component.append((cr, cc))
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                                visited[nr][nc] = True
                                stack.append((nr, nc))
                
                max_col = max(cc for cr, cc in component)
                
                row_cells = {}
                for cr, cc in component:
                    if cr not in row_cells:
                        row_cells[cr] = []
                    row_cells[cr].append(cc)
                
                for cr, cells in row_cells.items():
                    cells.sort(reverse=True)
                    stayed = set()
                    new_cells = []
                    
                    for cc in cells:
                        if cc + 1 > max_col or cc + 1 in stayed:
                            stayed.add(cc)
                            new_cells.append(cc)
                        else:
                            new_cells.append(cc + 1)
                    
                    for cc in new_cells:
                        output[cr][cc] = color
    
    return output
