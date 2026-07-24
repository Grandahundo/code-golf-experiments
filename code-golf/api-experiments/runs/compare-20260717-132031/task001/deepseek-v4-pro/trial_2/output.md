```python
def p(grid):
    """
    Maps an input grid to a 3x scaled output grid.
    For each cell (i, j) in the input, if the value is non-zero,
    a copy of the entire input grid is placed in the corresponding
    block of the output; otherwise that block is filled with zeros.
    """
    r = len(grid)
    c = len(grid[0])
    out_r = 3 * r
    out_c = 3 * c
    # Initialize output with zeros
    out = [[0] * out_c for _ in range(out_r)]
    
    for bi in range(r):
        for bj in range(c):
            if grid[bi][bj] != 0:
                # Copy input grid into block (bi, bj)
                for i in range(r):
                    for j in range(c):
                        out[bi * r + i][bj * c + j] = grid[i][j]
    return out
```