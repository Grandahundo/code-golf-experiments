```python
from collections import deque

def p(grid):
    rows = len(grid)
    if rows == 0:
        return grid
    cols = len(grid[0])
    
    visited = [[False] * cols for _ in range(rows)]
    components = []
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                val = grid[r][c]
                comp = []
                q = deque([(r, c)])
                visited[r][c] = True
                while q:
                    cr, cc = q.popleft()
                    comp.append((cr, cc))
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == val:
                                visited[nr][nc] = True
                                q.append((nr, nc))
                components.append((val, comp))
    
    output = [[0] * cols for _ in range(rows)]
    
    for val, comp in components:
        max_r = max(r for r, c in comp)
        max_c = max(c for r, c in comp)
        for r, c in comp:
            if r == max_r or c == max_c:
                output[r][c] = val
            else:
                output[r][c + 1] = val
    
    return output
```