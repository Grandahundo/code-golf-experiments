def p(grid):
    # Locate all cells of value 2 and 8
    twos = [(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] == 2]
    eights = [(r, c) for r in range(len(grid)) for c in range(len(grid[0])) if grid[r][c] == 8]

    if not twos or not eights:
        # No transformation without both shapes
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

    # Check overlaps in rows and columns
    rows_overlap = max(r_min2, r_min8) <= min(r_max2, r_max8)
    cols_overlap = max(c_min2, c_min8) <= min(c_max2, c_max8)

    dx = dy = 0

    if rows_overlap and not cols_overlap:
        # Horizontal movement
        if c_max2 < c_min8:          # 2 is left of 8
            dx = c_min8 - c_max2 - 1
        elif c_max8 < c_min2:        # 2 is right of 8
            dx = -(c_min2 - c_max8 - 1)
    elif cols_overlap and not rows_overlap:
        # Vertical movement
        if r_max2 < r_min8:          # 2 is above 8
            dy = r_min8 - r_max2 - 1
        elif r_max8 < r_min2:        # 2 is below 8
            dy = -(r_min2 - r_max8 - 1)
    else:
        # Ambiguous or overlapping – return original (should not occur in valid tasks)
        return [row[:] for row in grid]

    # Build output grid
    rows = len(grid)
    cols = len(grid[0])
    out = [[0] * cols for _ in range(rows)]

    # Place the fixed 8 shape
    for r, c in eights:
        out[r][c] = 8

    # Place the moved 2 shape
    for r, c in twos:
        nr = r + dy
        nc = c + dx
        out[nr][nc] = 2

    return out
