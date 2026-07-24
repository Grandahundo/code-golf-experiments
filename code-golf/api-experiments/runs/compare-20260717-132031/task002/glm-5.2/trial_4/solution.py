from collections import deque

def p(grid):
    if not grid or not grid[0]:
        return [row[:] for row in grid]
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]
    visited = [[False] * cols for _ in range(rows)]
    queue = deque()
    # Seed flood fill from border 0-cells
    for r in range(rows):
        for c in (0, cols - 1):
            if grid[r][c] == 0 and not visited[r][c]:
                visited[r][c] = True
                queue.append((r, c))
    for c in range(cols):
        for r in (0, rows - 1):
            if grid[r][c] == 0 and not visited[r][c]:
                visited[r][c] = True
                queue.append((r, c))
    # BFS through 0-cells
    while queue:
        r, c = queue.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if not visited[nr][nc] and grid[nr][nc] == 0:
                    visited[nr][nc] = True
                    queue.append((nr, nc))
    # Any 0-cell not reached from border is enclosed -> 4
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not visited[r][c]:
                output[r][c] = 4
    return output
