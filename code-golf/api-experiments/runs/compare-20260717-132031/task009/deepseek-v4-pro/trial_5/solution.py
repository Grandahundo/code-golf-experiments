def p(grid):
    R = len(grid)
    C = len(grid[0])
    L = grid[2][2]                         # line color
    H = (R + 2) // 3                       # number of block rows
    W = (C + 2) // 3                       # number of block columns
    
    # initialize block output and collect seeds
    B_out = [[0] * W for _ in range(H)]
    seeds = {}
    for i in range(H):
        r0 = 3 * i
        if r0 >= R: continue
        for j in range(W):
            c0 = 3 * j
            if c0 >= C: continue
            val = grid[r0][c0]
            if val != 0 and val != L:
                seeds.setdefault(val, []).append((i, j))
                B_out[i][j] = val           # place initial seed

    # for each value, perform row and column fills based on original seeds
    for V, pos_list in seeds.items():
        # row fill
        row_dict = {}
        for r, c in pos_list:
            row_dict.setdefault(r, []).append(c)
        for r, cols in row_dict.items():
            if len(cols) >= 2:
                c_min = min(cols)
                c_max = max(cols)
                for c in range(c_min, c_max + 1):
                    B_out[r][c] = V

        # column fill
        col_dict = {}
        for r, c in pos_list:
            col_dict.setdefault(c, []).append(r)
        for c, rows in col_dict.items():
            if len(rows) >= 2:
                r_min = min(rows)
                r_max = max(rows)
                for r in range(r_min, r_max + 1):
                    B_out[r][c] = V

    # construct final output grid
    out = [[0] * C for _ in range(R)]
    for r in range(R):
        for c in range(C):
            if r % 3 == 2 or c % 3 == 2:
                out[r][c] = L
            else:
                i = r // 3
                j = c // 3
                out[r][c] = B_out[i][j]
    return out
