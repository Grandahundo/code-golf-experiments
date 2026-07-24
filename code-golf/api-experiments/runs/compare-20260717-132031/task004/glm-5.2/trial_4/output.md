```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    visited = [[False] * cols for _ in range(rows)]
    shapes = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                stack = [(r, c)]
                visited[r][c] = True
                cells = []
                while stack:
                    cr, cc = stack.pop()
                    cells.append((cr, cc))
                    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nr, nc = cr + dr, cc + dc
                        if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                            visited[nr][nc] = True
                            stack.append((nr, nc))
                shapes.append((color, cells))

    output = [[0] * cols for _ in range(rows)]

    for color, cells in shapes:
        max_row = max(r for r, c in cells)
        max_col = max(c for r, c in cells)
        # Place stationary cells first (bottom row or rightmost column)
        for r, c in cells:
            if r == max_row or c == max_col:
                output[r][c] = color
        # Place shifted cells
        for r, c in cells:
            if not (r == max_row or c == max_col):
                output[r][c + 1] = color

    return output
```