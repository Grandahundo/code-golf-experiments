def p(grid):
    H = len(grid)
    W = len(grid[0])
    # Find the smallest period p such that the input rows follow the periodic pattern
    p_period = H
    for cand in range(1, H + 1):
        is_periodic = True
        for i in range(H):
            if grid[i] != grid[i % cand]:
                is_periodic = False
                break
        if is_periodic:
            p_period = cand
            break
    # Output height is input height + 3 (9 in the given examples)
    out_H = H + 3
    out_grid = []
    for i in range(out_H):
        src_row = grid[i % p_period]
        # Map 1 -> 2, keep 0 as 0
        out_row = [2 if val == 1 else 0 for val in src_row]
        out_grid.append(out_row)
    return out_grid
