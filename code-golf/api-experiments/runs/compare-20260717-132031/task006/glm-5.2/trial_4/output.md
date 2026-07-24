```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    sep = None
    for j in range(cols):
        if all(grid[i][j] == 5 for i in range(rows)):
            sep = j
            break
    if sep is None:
        return [row[:] for row in grid]
    left = [row[:sep] for row in grid]
    right = [row[sep+1:] for row in grid]
    out = []
    for i in range(rows):
        outrow = []
        for j in range(len(left[i])):
            if left[i][j] == 1 and right[i][j] == 1:
                outrow.append(2)
            else:
                outrow.append(0)
        out.append(outrow)
    return out
```