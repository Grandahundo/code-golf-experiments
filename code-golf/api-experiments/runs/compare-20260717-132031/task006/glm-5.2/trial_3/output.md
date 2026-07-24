```python
def p(grid):
    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])

    # Detect a vertical separator (a full column of 5s)
    sep_col = -1
    for c in range(cols):
        if all(grid[r][c] == 5 for r in range(rows)):
            sep_col = c
            break

    if sep_col != -1:
        left = [row[:sep_col] for row in grid]
        right = [row[sep_col + 1:] for row in grid]
        out = []
        for i in range(rows):
            out_row = []
            for j in range(len(left[i])):
                a = left[i][j]
                b = right[i][j] if j < len(right[i]) else 0
                out_row.append(2 if a == 1 and b == 1 else 0)
            out.append(out_row)
        return out

    # Detect a horizontal separator (a full row of 5s)
    sep_row = -1
    for r in range(rows):
        if all(grid[r][c] == 5 for c in range(cols)):
            sep_row = r
            break

    if sep_row != -1:
        top = grid[:sep_row]
        bottom = grid[sep_row + 1:]
        out = []
        for i in range(len(top)):
            out_row = []
            for j in range(len(top[i])):
                a = top[i][j]
                b = bottom[i][j] if i < len(bottom) and j < len(bottom[i]) else 0
                out_row.append(2 if a == 1 and b == 1 else 0)
            out.append(out_row)
        return out

    return grid
```