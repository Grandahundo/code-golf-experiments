```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    red_cells = []
    azure_cells = []
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v == 2:
                red_cells.append((r, c))
            elif v == 8:
                azure_cells.append((r, c))

    if not red_cells or not azure_cells:
        return [row[:] for row in grid]

    red_min_r = min(r for r, c in red_cells)
    red_max_r = max(r for r, c in red_cells)
    red_min_c = min(c for r, c in red_cells)
    red_max_c = max(c for r, c in red_cells)

    az_min_r = min(r for r, c in azure_cells)
    az_max_r = max(r for r, c in azure_cells)
    az_min_c = min(c for r, c in azure_cells)
    az_max_c = max(c for r, c in azure_cells)

    col_overlap = max(red_min_c, az_min_c) <= min(red_max_c, az_max_c)
    row_overlap = max(red_min_r, az_min_r) <= min(red_max_r, az_max_r)

    output = [row[:] for row in grid]
    for r, c in red_cells:
        output[r][c] = 0

    dr, dc = 0, 0
    if col_overlap:
        if red_max_r < az_min_r:
            dr = (az_min_r - 1) - red_max_r
        elif red_min_r > az_max_r:
            dr = (az_max_r + 1) - red_min_r
    elif row_overlap:
        if red_max_c < az_min_c:
            dc = (az_min_c - 1) - red_max_c
        elif red_min_c > az_max_c:
            dc = (az_max_c + 1) - red_min_c

    for r, c in red_cells:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            output[nr][nc] = 2

    return output
```