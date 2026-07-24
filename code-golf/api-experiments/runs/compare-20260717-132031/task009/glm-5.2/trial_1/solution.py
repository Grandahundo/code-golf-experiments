def p(grid):
    H = len(grid)
    W = len(grid[0]) if H else 0

    # Find the grid-line/border color: a full row of one nonzero color.
    C = None
    for row in grid:
        if row and all(x == row[0] for x in row) and row[0] != 0:
            C = row[0]
            break
    if C is None:
        cnt = {}
        for row in grid:
            for x in row:
                if x != 0:
                    cnt[x] = cnt.get(x, 0) + 1
        C = max(cnt, key=cnt.get) if cnt else 0

    # Rows/cols that are not solid grid lines are data rows/cols.
    data_rows = [r for r in range(H) if any(x != C for x in grid[r])]
    data_cols = [c for c in range(W) if any(grid[r][c] != C for r in range(H))]

    R = len(data_rows) // 2
    K = len(data_cols) // 2

    # Extract the NxN cell grid of 2x2 blocks.
    cell = [[0] * K for _ in range(R)]
    for i in range(R):
        r0 = data_rows[2 * i]
        r1 = data_rows[2 * i + 1]
        for j in range(K):
            c0 = data_cols[2 * j]
            c1 = data_cols[2 * j + 1]
            vals = [grid[r0][c0], grid[r0][c1], grid[r1][c0], grid[r1][c1]]
            nb = [v for v in vals if v != 0 and v != C]
            cell[i][j] = nb[0] if nb else 0

    out = [row[:] for row in cell]

    # Connect adjacent same-colored blocks in each row.
    for i in range(R):
        pts = [(j, cell[i][j]) for j in range(K) if cell[i][j] != 0]
        for a in range(len(pts) - 1):
            j1, c1 = pts[a]
            j2, c2 = pts[a + 1]
            if c1 == c2:
                for j in range(j1 + 1, j2):
                    if out[i][j] == 0 or out[i][j] == c1:
                        out[i][j] = c1

    # Connect adjacent same-colored blocks in each column.
    for j in range(K):
        pts = [(i, cell[i][j]) for i in range(R) if cell[i][j] != 0]
        for a in range(len(pts) - 1):
            i1, c1 = pts[a]
            i2, c2 = pts[a + 1]
            if c1 == c2:
                for i in range(i1 + 1, i2):
                    if out[i][j] == 0 or out[i][j] == c1:
                        out[i][j] = c1

    # Render changed cells back into the full grid.
    result = [row[:] for row in grid]
    for i in range(R):
        r0 = data_rows[2 * i]
        r1 = data_rows[2 * i + 1]
        for j in range(K):
            v = out[i][j]
            if v != cell[i][j]:
                c0 = data_cols[2 * j]
                c1 = data_cols[2 * j + 1]
                result[r0][c0] = v
                result[r0][c1] = v
                result[r1][c0] = v
                result[r1][c1] = v

    return result
