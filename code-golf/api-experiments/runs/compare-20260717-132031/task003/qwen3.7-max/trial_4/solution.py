def p(grid):
    rows = len(grid)
    period = rows
    for p in range(1, rows + 1):
        if all(grid[i] == grid[i + p] for i in range(rows - p)):
            period = p
            break
    target = rows + rows // 2
    return [[v * 2 for v in grid[i % period]] for i in range(target)]
