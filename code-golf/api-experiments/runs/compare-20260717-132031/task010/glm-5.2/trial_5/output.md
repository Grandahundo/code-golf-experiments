```python
def p(grid):
    if not grid:
        return []
    rows = len(grid)
    cols = len(grid[0]) if rows else 0
    col_starts = []
    for c in range(cols):
        for r in range(rows):
            if grid[r][c] == 5:
                col_starts.append((r, c))
                break
    col_starts.sort()
    color_map = {}
    for i, (r, c) in enumerate(col_starts):
        color_map[c] = i + 1
    out = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if grid[r][c] == 5:
                row.append(color_map[c])
            else:
                row.append(grid[r][c])
        out.append(row)
    return out
```