```python
def p(grid):
    n = len(grid)
    m = len(grid[0])
    sum_to_val = {}
    for i in range(n):
        for j in range(m):
            v = grid[i][j]
            if v != 0:
                s = i + j
                if s not in sum_to_val:
                    sum_to_val[s] = v
    if not sum_to_val:
        return [row[:] for row in grid]
    sorted_sums = sorted(sum_to_val.keys())
    seq_in = [sum_to_val[s] for s in sorted_sums]
    L = len(seq_in)
    min_sum = sorted_sums[0]
    r = min_sum % L
    if r == 0:
        seq_out = seq_in
    else:
        seq_out = seq_in[-r:] + seq_in[:-r]
    output = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            output[i][j] = seq_out[(i + j) % L]
    return output
```