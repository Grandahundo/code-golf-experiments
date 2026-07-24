```python
def p(grid):
    if not grid or not grid[0]:
        return []
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    out = [[0] * cols for _ in range(rows)]
    
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0 and not visited[i][j]:
                val = grid[i][j]
                comp = []
                queue = [(i, j)]
                visited[i][j] = True
                while queue:
                    r, c = queue.pop(0)
                    comp.append((r, c))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == val:
                            visited[nr][nc] = True
                            queue.append((nr, nc))
                max_r = max(r for r, _ in comp)
                max_c = max(c for _, c in comp)
                for r, c in comp:
                    if r == max_r or c == max_c:
                        nr, nc = r, c
                    else:
                        nr, nc = r, c + 1
                    out[nr][nc] = val
    return out
```