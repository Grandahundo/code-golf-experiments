def p(grid):
    """Task 008 (magnets): Slide red rectangle to be adjacent to cyan 2x2.
    The gap can be vertical or horizontal depending on flip/xpose.
    """
    H = len(grid)
    W = len(grid[0])

    reds = [(r, c) for r in range(H) for c in range(W) if grid[r][c] == 2]
    cyans = [(r, c) for r in range(H) for c in range(W) if grid[r][c] == 8]

    if not reds or not cyans:
        return [row[:] for row in grid]

    r_min = min(r for r, _ in reds)
    r_max = max(r for r, _ in reds)
    c_min = min(c for _, c in reds)
    c_max = max(c for _, c in reds)

    cy_rmin = min(r for r, _ in cyans)
    cy_rmax = max(r for r, _ in cyans)
    cy_cmin = min(c for _, c in cyans)
    cy_cmax = max(c for _, c in cyans)

    # Determine shift: red moves toward cyan to close the gap
    dr, dc = 0, 0

    if cy_cmin > c_max:
        # Cyan is to the right → shift red right
        gap = cy_cmin - c_max - 1
        dr, dc = 0, gap
    elif cy_cmax < c_min:
        # Cyan is to the left → shift red left
        gap = c_min - cy_cmax - 1
        dr, dc = 0, -gap
    elif cy_rmin > r_max:
        # Cyan is below → shift red down
        gap = cy_rmin - r_max - 1
        dr, dc = gap, 0
    elif cy_rmax < r_min:
        # Cyan is above → shift red up
        gap = r_min - cy_rmax - 1
        dr, dc = -gap, 0
    else:
        # Adjacent or overlapping (shouldn't happen, but be safe)
        # Check which gap is smaller
        v_gap = abs(cy_rmin - r_max) if cy_rmin > r_max else abs(r_min - cy_rmax)
        h_gap = abs(cy_cmin - c_max) if cy_cmin > c_max else abs(c_min - cy_cmax)
        if v_gap < h_gap:
            if cy_rmin > r_max:
                dr = cy_rmin - r_max - 1
            else:
                dr = -(r_min - cy_rmax - 1)
        else:
            if cy_cmin > c_max:
                dc = cy_cmin - c_max - 1
            else:
                dc = -(c_min - cy_cmax - 1)

    output = [row[:] for row in grid]

    # Erase old red
    for r, c in reds:
        output[r][c] = 0

    # Place shifted red
    for r, c in reds:
        nr, nc = r + dr, c + dc
        if 0 <= nr < H and 0 <= nc < W:
            output[nr][nc] = 2

    return output
