```python
def p(grid):
    R = len(grid)
    C = len(grid[0])
    out = [[0] * (C * C) for _ in range(R * R)]
    for br in range(R):
        for bc in range(C):
            if grid[br][bc] != 0:
                for ir in range(R):
                    row = out[br * R + ir]
                    src = grid[ir]
                    base = bc * C
                    for ic in range(C):
                        row[base + ic] = src[ic]
    return out
```