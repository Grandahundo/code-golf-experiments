def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    colors = []
    for row in grid:
        for v in row:
            if v and v not in colors:
                colors.append(v)

    period = len(colors) or 1
    seq = [None] * period

    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v:
                k = (r + c) % period
                if seq[k] is None:
                    seq[k] = v

    unused = [v for v in colors if v not in seq]
    u = 0
    for k in range(period):
        if seq[k] is None:
            seq[k] = unused[u] if u < len(unused) else 0
            u += 1

    return [[seq[(r + c) % period] for c in range(cols)] for r in range(rows)]
