def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    distinct_values = set()
    cells = []
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0:
                distinct_values.add(grid[i][j])
                cells.append((i, j, grid[i][j]))

    period = len(distinct_values)

    if period == 0:
        return [[0] * cols for _ in range(rows)]

    mapping = {}
    for i, j, v in cells:
        r = (i + j) % period
        mapping[r] = v

    output = []
    for i in range(rows):
        row = []
        for j in range(cols):
            r = (i + j) % period
            row.append(mapping.get(r, 0))
        output.append(row)

    return output
