def p(grid):
    if not grid:
        return []
    rows = len(grid)
    cols = len(grid[0])
    # Find the separator column (column where all values are 5)
    sep = None
    for c in range(cols):
        if all(grid[r][c] == 5 for r in range(rows)):
            sep = c
            break
    if sep is None:
        sep = cols // 2
    left = [row[:sep] for row in grid]
    right = [row[sep+1:] for row in grid]
    out = []
    for i in range(rows):
        outrow = []
        for j in range(len(left[i])):
            if left[i][j] == 1 and right[i][j] == 1:
                outrow.append(2)
            else:
                outrow.append(0)
        out.append(outrow)
    return out
