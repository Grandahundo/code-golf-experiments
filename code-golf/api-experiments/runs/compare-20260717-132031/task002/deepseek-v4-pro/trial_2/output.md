```python
import collections

def p(grid):
    if not grid:
        return []
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    output = [row[:] for row in grid]
    q = collections.deque()
    
    # Add all border zeros to the queue for flood fill
    for r in range(rows):
        for c in (0, cols - 1):
            if grid[r][c] == 0 and not visited[r][c]:
                visited[r][c] = True
                q.append((r, c))
    for c in range(cols):
        for r in (0, rows - 1):
            if grid[r][c] == 0 and not visited[r][c]:
                visited[r][c] = True
                q.append((r, c))
                
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    while q:
        r, c = q.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if grid[nr][nc] == 0 and not visited[nr][nc]:
                    visited[nr][nc] = True
                    q.append((nr, nc))
                    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not visited[r][c]:
                output[r][c] = 4
                
    return output
```