def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    # Find the separator column (all 5s)
    sep = None
    for c in range(cols):
        if all(grid[r][c] == 5 for r in range(rows)):
            sep = c
            break
    left = [[grid[r][c] for c in range(sep)] for r in range(rows)]
    right = [[grid[r][c] for c in range(sep + 1, cols)] for r in range(rows)]
    out = []
    for r in range(rows):
        row = []
        for c in range(len(left[r])):
            if left[r][c] != 0 and right[r][c] != 0:
                row.append(2)
            else:
                row.append(0)
        out.append(row)
    return out
