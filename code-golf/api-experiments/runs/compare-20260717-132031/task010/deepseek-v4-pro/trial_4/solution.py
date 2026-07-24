from collections import deque

def p(grid):
    if not grid or not grid[0]:
        return []
    rows = len(grid)
    cols = len(grid[0])
    visited = [[False] * cols for _ in range(rows)]
    components = []  # list of (min_r, min_c, cells)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                # BFS for this component
                comp_cells = []
                min_r, min_c = r, c
                q = deque()
                q.append((r, c))
                visited[r][c] = True
                while q:
                    cr, cc = q.popleft()
                    comp_cells.append((cr, cc))
                    if cr < min_r:
                        min_r = cr
                        min_c = cc
                    elif cr == min_r and cc < min_c:
                        min_c = cc
                    for dr, dc in directions:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            if grid[nr][nc] != 0 and not visited[nr][nc]:
                                visited[nr][nc] = True
                                q.append((nr, nc))
                components.append((min_r, min_c, comp_cells))

    # Sort components by min_r, then min_c
    components.sort(key=lambda x: (x[0], x[1]))

    # Create output grid
    output = [[0] * cols for _ in range(rows)]
    for label, (_, _, cells) in enumerate(components, start=1):
        for r, c in cells:
            output[r][c] = label

    return output
