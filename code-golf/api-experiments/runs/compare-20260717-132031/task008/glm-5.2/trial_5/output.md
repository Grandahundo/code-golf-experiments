```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    red_cells = []
    azure_cells = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                red_cells.append((r, c))
            elif grid[r][c] == 8:
                azure_cells.append((r, c))

    if not red_cells or not azure_cells:
        return [row[:] for row in grid]

    red_rows = [r for r, c in red_cells]
    red_cols = [c for r, c in red_cells]
    azure_rows = [r for r, c in azure_cells]
    azure_cols = [c for r, c in azure_cells]

    red_rmin, red_rmax = min(red_rows), max(red_rows)
    red_cmin, red_cmax = min(red_cols), max(red_cols)
    az_rmin, az_rmax = min(azure_rows), max(azure_rows)
    az_cmin, az_cmax = min(azure_cols), max(azure_cols)

    output = []
    for r in range(rows):
        new_row = []
        for c in range(cols):
            if grid[r][c] == 2:
                new_row.append(0)
            else:
                new_row.append(grid[r][c])
        output.append(new_row)

    col_overlap = not (red_cmax < az_cmin or az_cmax < red_cmin)
    row_overlap = not (red_rmax < az_rmin or az_rmax < red_rmin)

    new_dr = 0
    new_dc = 0

    if col_overlap and not row_overlap:
        if red_rmax < az_rmin:
            new_dr = az_rmin - red_rmax - 1
        else:
            new_dr = -(red_rmin - az_rmax - 1)
    elif row_overlap and not col_overlap:
        if red_cmax < az_cmin:
            new_dc = az_cmin - red_cmax - 1
        else:
            new_dc = -(red_cmin - az_cmax - 1)

    for r, c in red_cells:
        output[r + new_dr][c + new_dc] = 2

    return output
```