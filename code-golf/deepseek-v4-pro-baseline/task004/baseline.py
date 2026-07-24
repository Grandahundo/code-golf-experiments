def p(grid):
    """Transform the input grid by shifting each parallelogram's
    top edge and left diagonal right by 1 pixel."""
    height = len(grid)
    width = len(grid[0])

    # Collect all non-zero pixels
    pixels = set()
    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0:
                pixels.add((r, c))

    # Group into connected components (8-directional)
    components = []
    visited = set()

    for r, c in pixels:
        if (r, c) in visited:
            continue
        # BFS this component
        comp = set()
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if (cr, cc) in visited:
                continue
            visited.add((cr, cc))
            comp.add((cr, cc))
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width:
                        if grid[nr][nc] != 0 and (nr, nc) not in visited:
                            stack.append((nr, nc))
        components.append(comp)

    # Build output from scratch
    output = [[0] * width for _ in range(height)]

    for comp in components:
        # Group pixels by row
        rows = {}
        for cr, cc in comp:
            rows.setdefault(cr, []).append(cc)

        min_row = min(rows)
        max_row = max(rows)
        overall_max_col = max(max(cols) for cols in rows.values())

        for cr, cols in rows.items():
            cols.sort()
            left_col = cols[0]
            right_col = cols[-1]

            if cr == min_row:
                # Top edge: every pixel shifts right by 1
                for cc in cols:
                    if cc + 1 < width:
                        output[cr][cc + 1] = grid[cr][cc]
            elif cr == max_row:
                # Bottom edge: no shift
                for cc in cols:
                    output[cr][cc] = grid[cr][cc]
            else:
                # Middle rows: left pixel shifts right; right pixel
                # shifts right unless it's already at the shape's
                # rightmost column
                output[cr][left_col + 1] = grid[cr][left_col]
                if right_col < overall_max_col:
                    output[cr][right_col + 1] = grid[cr][right_col]
                else:
                    output[cr][right_col] = grid[cr][right_col]

    return output
