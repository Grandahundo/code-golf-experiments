def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows else 0

    red = []
    azure = []
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v == 2:
                red.append((r, c))
            elif v == 8:
                azure.append((r, c))

    out = [row[:] for row in grid]
    if not red or not azure:
        return out

    candidates = []
    for r, c in red:
        for a, b in azure:
            if c == b:
                if a > r:
                    d = a - r - 1
                    if d >= 0:
                        candidates.append((d, d, 0))
                elif a < r:
                    d = r - a - 1
                    if d >= 0:
                        candidates.append((d, -d, 0))
            if r == a:
                if b > c:
                    d = b - c - 1
                    if d >= 0:
                        candidates.append((d, 0, d))
                elif b < c:
                    d = c - b - 1
                    if d >= 0:
                        candidates.append((d, 0, -d))

    if candidates:
        _, dr, dc = min(candidates, key=lambda x: (x[0], 0 if x[1] != 0 else 1))
    else:
        def bbox(coords):
            rs = [r for r, _ in coords]
            cs = [c for _, c in coords]
            return min(rs), max(rs), min(cs), max(cs)

        rmin, rmax, cmin, cmax = bbox(red)
        amin, amax, bmin, bmax = bbox(azure)

        moves = []
        if rmax < amin:
            d = amin - rmax - 1
            moves.append((d, d, 0))
        elif rmin > amax:
            d = rmin - amax - 1
            moves.append((d, -d, 0))
        if cmax < bmin:
            d = bmin - cmax - 1
            moves.append((d, 0, d))
        elif cmin > bmax:
            d = cmin - bmax - 1
            moves.append((d, 0, -d))

        if moves:
            _, dr, dc = min(moves, key=lambda x: x[0])
        else:
            dr, dc = 0, 0

    for r, c in red:
        out[r][c] = 0
    for r, c in red:
        nr, nc = r + dr, c + dc
        if 0 <= nr < rows and 0 <= nc < cols:
            out[nr][nc] = 2

    return out
