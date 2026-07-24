def p(grid):
    n = len(grid)
    result = []
    for i in range(n):
        for r in range(n):
            row = []
            for j in range(n):
                if grid[i][j] != 0:
                    row.extend(grid[r])
                else:
                    row.extend([0] * n)
            result.append(row)
    return result
