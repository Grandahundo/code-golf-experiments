def p(input_grid):
    h = len(input_grid)
    w = len(input_grid[0])

    out_h = h * h
    out_w = w * w
    output = [[0] * out_w for _ in range(out_h)]

    for i in range(h):
        for j in range(w):
            if input_grid[i][j] != 0:
                for r in range(h):
                    for c in range(w):
                        output[i * h + r][j * w + c] = input_grid[r][c]

    return output