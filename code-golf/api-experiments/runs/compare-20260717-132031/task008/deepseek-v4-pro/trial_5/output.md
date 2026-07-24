```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # Collect coordinates of 2 and 8 cells
    twos = []
    eights = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                twos.append((r, c))
            elif grid[r][c] == 8:
                eights.append((r, c))

    # If either shape is missing, return the grid unchanged
    if not twos or not eights:
        return [row[:] for row in grid]

    # Bounding boxes
    r_min2 = min(r for r, _ in twos)
    r_max2 = max(r for r, _ in twos)
    c_min2 = min(c for _, c in twos)
    c_max2 = max(c for _, c in twos)

    r_min8 = min(r for r, _ in eights)
    r_max8 = max(r for r, _ in eights)
    c_min8 = min(c for _, c in eights)
    c_max8 = max(c for _, c in eights)

    # Determine overlap along each axis
    col_overlap = not (c_max2 < c_min8 or c_max8 < c_min2)
    row_overlap = not (r_max2 < r_min8 or r_max8 < r_min2)

    dr = 0
    dc = 0

    if col_overlap and not row_overlap:
        # Vertical movement
        if r_max2 < r_min8:
            # 2 is above 8, move down
            gap = r_min8 - r_max2 - 1
            dr = gap
        else:
            # 2 is below 8, move up
            gap = r_min2 - r_max8 - 1
            dr = -gap
    elif row_overlap and not col_overlap:
        # Horizontal movement
        if c_max2 < c_min8:
            # 2 is left of 8, move right
            gap = c_min8 - c_max2 - 1
            dc = gap
        else:
            # 2 is right of 8, move left
            gap = c_min2 - c_max8 - 1
            dc = -gap
    else:
        # Overlapping or no clear axis – no movement
        return [row[:] for row in grid]

    # Build output grid
    out = [[0] * cols for _ in range(rows)]
    for r, c in eights:
        out[r][c] = 8
    for r, c in twos:
        nr = r + dr
        nc = c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            out[nr][nc] = 2
        # If out of bounds, ignore (should not happen for valid inputs)

    return out
```