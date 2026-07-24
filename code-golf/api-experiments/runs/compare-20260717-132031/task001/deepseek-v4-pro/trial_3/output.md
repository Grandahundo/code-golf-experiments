```python
def p(grid):
    """Transform input grid to output grid by tiling: at block (i,j) if grid[i][j]!=0, place full grid, else zeros."""
    n = len(grid)
    m = len(grid[0]) if n > 0 else 0
    # output size will be n*n by m*m (assuming square-like but generalizing for rectangular, though examples are square)
    out_rows = n * n
    out_cols = m * m if n > 0 else 0
    output = [[0] * out_cols for _ in range(out_rows)]
    for i in range(n):
        for j in range(m):
            if grid[i][j] != 0:
                # copy entire input grid into the corresponding block
                for r in range(n):
                    for c in range(m):
                        output[i*n + r][j*m + c] = grid[r][c]
    return output
```