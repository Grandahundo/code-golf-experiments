def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    ext = rows // 2

    def find_period(col):
        n = len(col)
        for period in range(1, n + 1):
            if all(col[i] == col[i % period] for i in range(period, n)):
                return period
        return n

    columns = []
    periods = []
    for c in range(cols):
        col = [grid[r][c] for r in range(rows)]
        columns.append(col)
        periods.append(find_period(col))

    result = []
    for r in range(rows + ext):
        row = []
        for c in range(cols):
            val = columns[c][r % periods[c]]
            row.append(2 if val == 1 else val)
        result.append(row)

    return result
