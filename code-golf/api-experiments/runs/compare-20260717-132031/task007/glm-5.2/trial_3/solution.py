def p(grid):
    color_by_residue = {}
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            if v != 0:
                r = (i + j) % 3
                if r not in color_by_residue:
                    color_by_residue[r] = v
    return [
        [color_by_residue.get((i + j) % 3, 0) for j in range(len(row))]
        for i, row in enumerate(grid)
    ]
