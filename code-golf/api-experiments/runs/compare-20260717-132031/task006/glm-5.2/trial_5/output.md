```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    sep = -1
    for c in range(cols):
        if all(grid[r][c] == 5 for r in range(rows)):
            sep = c
            break
    left = [row[:sep] for row in grid]
    right = [row[sep+1:] for row in grid]
    w = len(left[0])
    output = []
    for i in range(rows):
        out_row = []
        for j in range(w):
            if left[i][j] == 1 and right[i][j] == 1:
                out_row.append(2)
            else:
                out_row.append(0)
        output.append(out_row)
    return output
```