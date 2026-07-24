def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    lines = []
    for c in range(cols):
        r = 0
        while r < rows:
            if grid[r][c] == 5:
                start = r
                while r < rows and grid[r][c] == 5:
                    r += 1
                length = r - start
                lines.append((length, c, start))
            else:
                r += 1
    # Sort by length descending; stable sort keeps column order for ties
    lines_sorted = sorted(lines, key=lambda x: -x[0])
    out = [row[:] for row in grid]
    for i, (length, c, start) in enumerate(lines_sorted):
        color = i + 1
        for r in range(start, start + length):
            out[r][c] = color
    return out
