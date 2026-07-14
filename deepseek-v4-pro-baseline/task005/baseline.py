def p(grid):
    """Task 005 (stamp): Stamp a 3x3 sprite outward in multiple directions.
    The input shows the full sprite at center and leading-edge pixels
    of the first stamp in each direction. Step between stamps is 4.
    """
    H = len(grid)
    W = len(grid[0])

    # Find all non-zero pixels
    pixels = [(r, c, grid[r][c]) for r in range(H) for c in range(W) if grid[r][c]]

    if not pixels:
        return [row[:] for row in grid]

    # Group into connected components (8-directional)
    all_positions = set((r, c) for r, c, _ in pixels)
    color_of = {(r, c): grid[r][c] for r, c in all_positions}
    visited = set()
    components = []

    for r, c in all_positions:
        if (r, c) in visited:
            continue
        comp = []
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if (cr, cc) in visited:
                continue
            visited.add((cr, cc))
            comp.append((cr, cc, color_of[(cr, cc)]))
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = cr + dr, cc + dc
                    if (nr, nc) in all_positions and (nr, nc) not in visited:
                        stack.append((nr, nc))
        components.append(comp)

    # Find the center sprite: the component whose bounding box is ~3x3
    # and has the most pixels
    def bbox(comp):
        rs = [p[0] for p in comp]
        cs = [p[1] for p in comp]
        return min(rs), min(cs), max(rs), max(cs)

    # Sort by size, largest is the center sprite
    components.sort(key=len, reverse=True)
    center = components[0]
    min_r, min_c, max_r, max_c = bbox(center)
    sprite = [(r - min_r, c - min_c) for r, c, _ in center]
    srow, scol = min_r, min_c  # top-left of the sprite

    output = [[0] * W for _ in range(H)]

    # Stamp function
    def stamp(out, top, left, color):
        for dr, dc in sprite:
            r, c = top + dr, left + dc
            if 0 <= r < H and 0 <= c < W:
                out[r][c] = color

    # Stamp the center sprite (color from center component)
    center_color = center[0][2]
    stamp(output, srow, scol, center_color)

    # For each other component, determine direction and stamp repeatedly
    for comp in components[1:]:
        if not comp:
            continue
        comp_color = comp[0][2]
        cmin_r, cmin_c, _, _ = bbox(comp)

        # Direction: offset from center
        dr = cmin_r - srow
        dc = cmin_c - scol

        # The first stamp is at (srow + 4*rdir, scol + 4*cdir)
        # So rdir = dr // 4, cdir = dc // 4
        # Handle the case where the offset might not be exactly divisible by 4
        # Just find the best matching direction
        best_dir = None
        best_match = 0
        for rdir in (-1, 0, 1):
            for cdir in (-1, 0, 1):
                if rdir == 0 and cdir == 0:
                    continue
                # First stamp center position
                fsr = srow + 4 * rdir
                fsc = scol + 4 * cdir
                # Check overlap with this component
                comp_set = set((r, c) for r, c, _ in comp)
                match = 0
                for dr2, dc2 in sprite:
                    pr, pc = fsr + dr2, fsc + dc2
                    if (pr, pc) in comp_set:
                        match += 1
                if match > best_match:
                    best_match = match
                    best_dir = (rdir, cdir)

        if best_dir is None:
            continue
        rdir, cdir = best_dir

        # Stamp repeatedly in this direction
        row, col = srow + 4 * rdir, scol + 4 * cdir
        while True:
            if row < -5 or row > H or col < -5 or col > W:
                break
            stamp(output, row, col, comp_color)
            row += 4 * rdir
            col += 4 * cdir

    return output
