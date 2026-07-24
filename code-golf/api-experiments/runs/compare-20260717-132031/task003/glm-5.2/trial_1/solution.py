def p(grid):
    n = len(grid)
    # Find smallest vertical period
    period = n
    for P in range(1, n + 1):
        valid = True
        for i in range(n):
            if grid[i] != grid[i % P]:
                valid = False
                break
        if valid:
            period = P
            break
    # Output length is 1.5x input length
    out_len = 3 * n // 2
    # Build output with color change 1 -> 2
    result = []
    for i in range(out_len):
        row = [2 if x == 1 else x for x in grid[i % period]]
        result.append(row)
    return result
