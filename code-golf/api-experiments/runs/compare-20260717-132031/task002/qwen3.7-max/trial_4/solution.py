from collections import deque

def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    visited = [[False] * cols for _ in range(rows)]
    queue = deque()
    
    # Seed BFS from all 0-cells on the grid border
    for r in range(rows):
        for c in range(cols):
            if (r == 0 or r == rows - 1 or c == 0 or c == cols - 1):
                if grid[r][c] == 0:
                    queue.append((r, c))
                    visited[r][c] = True
    
    # BFS flood fill through connected 0-cells
    while queue:
        r, c = queue.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if not visited[nr][nc] and grid[nr][nc] == 0:
                    visited[nr][nc] = True
                    queue.append((nr, nc))
    
    # Build output: enclosed 0-cells (not visited) become 4
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if grid[r][c] == 0 and not visited[r][c]:
                row.append(4)
            else:
                row.append(grid[r][c])
        output.append(row)
    
    return output
