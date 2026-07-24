```python
def p(grid):
    n = len(grid)
    m = len(grid[0]) if n else 0
    out = [[0] * (3 * m) for _ in range(3 * n)]
    for bi in range(3):
        for bj in range(3):
            if bi < n and bj < m and grid[bi][bj] != 0:
                for i in range(n):
                    out_row = out[bi * n + i]
                    src_row = grid[i]
                    base = bj * m
                    for j in range(m):
                        out_row[base + j] = src_row[j]
    return out
```