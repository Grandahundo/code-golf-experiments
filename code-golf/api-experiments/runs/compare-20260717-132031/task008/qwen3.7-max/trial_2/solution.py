def p(grid):
    rows = len(grid)
    cols = len(grid[0])

    cells_2 = []
    cells_8 = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                cells_2.append((r, c))
            elif grid[r][c] == 8:
                cells_8.append((r, c))

    if not cells_2 or not cells_8:
        return [row[:] for row in grid]

    min_r2 = min(r for r, c in cells_2)
    max_r2 = max(r for r, c in cells_2)
    min_c2 = min(c for r, c in cells_2)
    max_c2 = max(c for r, c in cells_2)

    min_r8 = min(r for r, c in cells_8)
    max_r8 = max(r for r, c in cells_8)
    min_c8 = min(c for r, c in cells_8)
    max_c8 = max(c for r, c in cells_8)

    dr = 0
    dc = 0

    if max_r2 < min_r8:
        # 2s above 8s -> move down
        cols_2 = set(c for r, c in cells_2)
        cols_8 = set(c for r, c in cells_8)
        min_gap = float('inf')
        for c in cols_2 & cols_8:
            r2_max = max(r for r, cc in cells_2 if cc == c)
            r8_min = min(r for r, cc in cells_8 if cc == c)
            min_gap = min(min_gap, r8_min - r2_max - 1)
        dr = min_gap
    elif min_r2 > max_r8:
        # 2s below 8s -> move up
        cols_2 = set(c for r, c in cells_2)
        cols_8 = set(c for r, c in cells_8)
        min_gap = float('inf')
        for c in cols_2 & cols_8:
            r2_min = min(r for r, cc in cells_2 if cc == c)
            r8_max = max(r for r, cc in cells_8 if cc == c)
            min_gap = min(min_gap, r2_min - r8_max - 1)
        dr = -min_gap
    elif max_c2 < min_c8:
        # 2s left of 8s -> move right
        rows_2 = set(r for r, c in cells_2)
        rows_8 = set(r for r, c in cells_8)
        min_gap = float('inf')
        for r in rows_2 & rows_8:
            c2_max = max(c for rr, c in cells_2 if rr == r)
            c8_min = min(c for rr, c in cells_8 if rr == r)
            min_gap = min(min_gap, c8_min - c2_max - 1)
        dc = min_gap
    elif min_c2 > max_c8:
        # 2s right of 8s -> move left
        rows_2 = set(r for r, c in cells_2)
        rows_8 = set(r for r, c in cells_8)
        min_gap = float('inf')
        for r in rows_2 & rows_8:
            c2_min = min(c for rr, c in cells_2 if rr == r)
            c8_max = max(c for rr, c in cells_8 if rr == r)
            min_gap = min(min_gap, c2_min - c8_max - 1)
        dc = -min_gap

    output = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 2:
                output[r][c] = grid[r][c]
    for r, c in cells_2:
        output[r + dr][c + dc] = 2

    return output
