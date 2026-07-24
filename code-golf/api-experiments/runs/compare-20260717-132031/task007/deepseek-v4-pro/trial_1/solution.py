def p(grid):
    n = len(grid)
    m = len(grid[0])
    sum_to_val = {}
    for i in range(n):
        for j in range(m):
            v = grid[i][j]
            if v != 0:
                s = i + j
                sum_to_val[s] = v  # all non-zero on same anti-diagonal share the same value
    if not sum_to_val:
        return [[0] * m for _ in range(n)]
    sums = sorted(sum_to_val.keys())
    values = [sum_to_val[s] for s in sums]
    L = len(values)
    s0 = sums[0]
    offset = s0 % L
    output = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            output[i][j] = values[(i + j - offset) % L]
    return output
