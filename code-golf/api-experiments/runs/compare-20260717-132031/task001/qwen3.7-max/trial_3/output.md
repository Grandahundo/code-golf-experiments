```python
def p(grid):
    n = len(grid)
    m = len(grid[0])
    output = [[0] * (m * m) for _ in range(n * n)]
    for i in range(n):
        for j in range(m):
            if grid[i][j] != 0:
                for di in range(n):
                    for dj in range(m):
                        output[i * n + di][j * m + dj] = grid[di][dj]
    return output
```