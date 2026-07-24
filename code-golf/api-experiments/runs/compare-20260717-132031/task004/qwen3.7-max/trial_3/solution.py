from collections import deque

def p(grid):
    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])
    if cols == 0:
        return [[] for _ in range(rows)]
    
    output = [[0] * cols for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                value = grid[r][c]
                component = []
                queue = deque([(r, c)])
                visited[r][c] = True
                while queue:
                    cr, cc = queue.popleft()
                    component.append((cr, cc))
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < rows and 0 <= nc < cols:
                                if not visited[nr][nc] and grid[nr][nc] == value:
                                    visited[nr][nc] = True
                                    queue.append((nr, nc))
                
                max_col = max(cc for cr, cc in component)
                
                row_cells = {}
                for cr, cc in component:
                    if cr not in row_cells:
                        row_cells[cr] = []
                    row_cells[cr].append(cc)
                
                for row in row_cells:
                    cells = sorted(row_cells[row], reverse=True)
                    occupied = set()
                    for cc in cells:
                        new_c = cc + 1
                        if new_c > max_col or new_c in occupied:
                            new_c = cc
                        occupied.add(new_c)
                        output[row][new_c] = value
    
    return output
