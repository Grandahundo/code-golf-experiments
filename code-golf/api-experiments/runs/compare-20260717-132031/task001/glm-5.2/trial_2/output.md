```python
def p(grid):
    R = len(grid)
    C = len(grid[0]) if R > 0 else 0
    out = [[0] * (C * C) for _ in range(R * R)]
    for br in range(R):
        for bc in range(C):
            if grid[br][bc] != 0:
                for i in range(R):
                    for j in range(C):
                        out[br * R + i][bc * C + j] = grid[i][j]
    return out
```