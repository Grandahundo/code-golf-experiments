```python
from collections import deque

def p(grid):
    if not grid or not grid[0]:
        return []
    R = len(grid)
    C = len(grid[0])
    # visited array for 0 cells reachable from border
    visited = [[False] * C for _ in range(R)]
    q = deque()
    
    # Initialize queue with all border 0 cells
    for i in range(R):
        for j in [0, C-1]:
            if grid[i][j] == 0:
                visited[i][j] = True
                q.append((i, j))
    for j in range(C):
        for i in [0, R-1]:
            if grid[i][j] == 0:
                visited[i][j] = True
                q.append((i, j))
    
    # BFS/DFS to mark all reachable 0s
    dirs = [(1,0), (-1,0), (0,1), (0,-1)]
    while q:
        r, c = q.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                if grid[nr][nc] == 0 and not visited[nr][nc]:
                    visited[nr][nc] = True
                    q.append((nr, nc))
    
    # Build output grid
    output = [[0] * C for _ in range(R)]
    for i in range(R):
        for j in range(C):
            if grid[i][j] == 3:
                output[i][j] = 3
            elif grid[i][j] == 0:
                if visited[i][j]:
                    output[i][j] = 0
                else:
                    output[i][j] = 4
            else:
                output[i][j] = grid[i][j]  # preserve any other numbers (though not present)
    return output
```