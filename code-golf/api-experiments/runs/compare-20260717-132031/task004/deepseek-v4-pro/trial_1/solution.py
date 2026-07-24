def p(grid):
    h = len(grid)
    w = len(grid[0])
    visited = [[False] * w for _ in range(h)]
    output = [[0] * w for _ in range(h)]

    # 8-connectivity directions
    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)]

    for i in range(h):
        for j in range(w):
            if grid[i][j] != 0 and not visited[i][j]:
                # collect this connected component (8-connected)
                component = []
                stack = [(i, j)]
                visited[i][j] = True
                val = grid[i][j]
                while stack:
                    r, c = stack.pop()
                    component.append((r, c))
                    for dr, dc in dirs:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < h and 0 <= nc < w and not visited[nr][nc] and grid[nr][nc] == val:
                            visited[nr][nc] = True
                            stack.append((nr, nc))

                # group columns by row
                by_row = {}
                for r, c in component:
                    by_row.setdefault(r, []).append(c)

                # bottom row of this component
                bottom_r = max(by_row.keys())
                L_b = min(by_row[bottom_r])
                R_b = max(by_row[bottom_r])

                # apply transformation for each row
                for r, cols in by_row.items():
                    cols.sort()
                    L_r = min(cols)
                    R_r = max(cols)
                    if r == bottom_r:
                        s = 0
                        Lp = L_b
                        Rp = R_b
                    else:
                        s = 1
                        Lp = min(L_b, L_r + 1)
                        Rp = min(R_b, R_r + 1)

                    for c in cols:
                        nc = c + s
                        if nc < Lp:
                            nc = Lp
                        elif nc > Rp:
                            nc = Rp
                        output[r][nc] = val

    return output
