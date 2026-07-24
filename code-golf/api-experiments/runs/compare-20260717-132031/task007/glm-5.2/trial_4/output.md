```python
def p(grid):
    color_map = {}
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] != 0:
                color_map[(r + c) % 3] = grid[r][c]
    rows = len(grid)
    cols = len(grid[0])
    return [[color_map[(i + j) % 3] for j in range(cols)] for i in range(rows)]
```