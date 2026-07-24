```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # Collect coordinates of all 2s and 8s
    twos = []
    eights = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                twos.append((r, c))
            elif grid[r][c] == 8:
                eights.append((r, c))

    if not twos or not eights:
        # No transformation possible, return a copy
        return [row[:] for row in grid]

    # Bounding boxes
    min_r2 = min(r for r, c in twos)
    max_r2 = max(r for r, c in twos)
    min_c2 = min(c for r, c in twos)
    max_c2 = max(c for r, c in twos)

    min_r8 = min(r for r, c in eights)
    max_r8 = max(r for r, c in eights)
    min_c8 = min(c for r, c in eights)
    max_c8 = max(c for r, c in eights)

    # Overlap tests
    row_overlap = not (max_r2 < min_r8 or max_r8 < min_r2)
    col_overlap = not (max_c2 < min_c8 or max_c8 < min_c2)

    dr = 0
    dc = 0

    if col_overlap and not row_overlap:
        # Move vertically
        if max_r2 < min_r8:          # 2 above 8
            dr = min_r8 - 1 - max_r2
        elif min_r2 > max_r8:        # 2 below 8
            dr = max_r8 + 1 - min_r2
    elif row_overlap and not col_overlap:
        # Move horizontally
        if max_c2 < min_c8:          # 2 left of 8
            dc = min_c8 - 1 - max_c2
        elif min_c2 > max_c8:        # 2 right of 8
            dc = max_c8 + 1 - min_c2
    # else: both overlap or neither overlap -> no movement

    # Build output grid
    out = [[0] * cols for _ in range(rows)]

    # Place 8s (unchanged)
    for r, c in eights:
        out[r][c] = 8

    # Place 2s shifted
    for r, c in twos:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            out[nr][nc] = 2

    return out
```