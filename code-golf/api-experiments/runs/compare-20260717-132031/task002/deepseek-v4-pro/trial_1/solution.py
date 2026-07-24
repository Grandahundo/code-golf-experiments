from collections import deque

def p(grid):
    if not grid or not grid[0]:
        return grid
    h = len(grid)
    w = len(grid[0])
    # copy grid to avoid modifying original while reading
    result = [row[:] for row in grid]
    visited = [[False] * w for _ in range(h)]

    q = deque()
    # Add all border zeros to the queue
    for i in range(h):
        for j in (0, w - 1):
            if result[i][j] == 0 and not visited[i][j]:
                visited[i][j] = True
                q.append((i, j))
    for j in range(w):
        for i in (0, h - 1):
            if result[i][j] == 0 and not visited[i][j]:
                visited[i][j] = True
                q.append((i, j))

    # BFS/DFS to mark all zeros reachable from the border
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while q:
        r, c = q.popleft()
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w:
                if result[nr][nc] == 0 and not visited[nr][nc]:
                    visited[nr][nc] = True
                    q.append((nr, nc))

    # All unvisited zeros become 4
    for i in range(h):
        for j in range(w):
            if result[i][j] == 0 and not visited[i][j]:
                result[i][j] = 4

    return result
