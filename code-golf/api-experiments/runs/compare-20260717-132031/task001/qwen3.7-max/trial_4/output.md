```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    out_rows = rows * rows
    out_cols = cols * cols
    output = [[0] * out_cols for _ in range(out_rows)]
    for br in range(rows):
        for bc in range(cols):
            if grid[br][bc] != 0:
                for r in range(rows):
                    for c in range(cols):
                        output[br * rows + r][bc * cols + c] = grid[r][c]
    return output
```