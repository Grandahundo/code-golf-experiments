def p(grid):
    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    output = [row[:] for row in grid]
    
    reachable = [[False] * cols for _ in range(rows)]
    stack = []
    
    for r in range(rows):
        for c in [0, cols - 1]:
            if grid[r][c] == 0 and not reachable[r][c]:
                reachable[r][c] = True
                stack.append((r, c))
    for c in range(cols):
        for r in [0, rows - 1]:
            if grid[r][c] == 0 and not reachable[r][c]:
                reachable[r][c] = True
                stack.append((r, c))
    
    while stack:
        r, c = stack.pop()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0 and not reachable[nr][nc]:
                reachable[nr][nc] = True
                stack.append((nr, nc))
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 0 and not reachable[r][c]:
                output[r][c] = 4
    
    return output
