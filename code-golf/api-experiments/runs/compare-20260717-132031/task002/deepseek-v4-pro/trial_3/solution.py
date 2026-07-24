from collections import deque

def p(grid):
    """
    Transforms the input grid by filling interior holes (0-cells completely enclosed by 3-cells)
    with the value 4. Interior holes are 0-cells that are not reachable from the grid boundary
    via orthogonal moves through other 0-cells.
    """
    if not grid or not grid[0]:
        return grid

    rows, cols = len(grid), len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    q = deque()

    # Add all boundary 0-cells to the queue
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

    # BFS to mark all 0-cells reachable from the boundary
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    while q:
        r, c = q.popleft()
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if not visited[nr][nc] and grid[nr][nc] == 0:
                    visited[nr][nc] = True
                    q.append((nr, nc))

    # Build output: interior 0-cells become 4, everything else stays the same
    output = [row[:] for row in grid]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not visited[r][c]:
                output[r][c] = 4

    return output
