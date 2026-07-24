import collections

def p(grid):
    """
    Transforms the input grid by filling all 0-cells that are not connected
    to the border (via 4-directional moves) with the value 4.
    """
    if not grid:
        return grid
    height = len(grid)
    width = len(grid[0])
    output = [row[:] for row in grid]  # copy
    visited = [[False] * width for _ in range(height)]

    # BFS from all border 0-cells
    q = collections.deque()
    for i in range(height):
        if grid[i][0] == 0 and not visited[i][0]:
            q.append((i, 0))
            visited[i][0] = True
        if grid[i][width - 1] == 0 and not visited[i][width - 1]:
            q.append((i, width - 1))
            visited[i][width - 1] = True
    for j in range(width):
        if grid[0][j] == 0 and not visited[0][j]:
            q.append((0, j))
            visited[0][j] = True
        if grid[height - 1][j] == 0 and not visited[height - 1][j]:
            q.append((height - 1, j))
            visited[height - 1][j] = True

    dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while q:
        r, c = q.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < height and 0 <= nc < width:
                if grid[nr][nc] == 0 and not visited[nr][nc]:
                    visited[nr][nc] = True
                    q.append((nr, nc))

    # Fill interior (unvisited 0-cells) with 4
    for i in range(height):
        for j in range(width):
            if grid[i][j] == 0 and not visited[i][j]:
                output[i][j] = 4

    return output
