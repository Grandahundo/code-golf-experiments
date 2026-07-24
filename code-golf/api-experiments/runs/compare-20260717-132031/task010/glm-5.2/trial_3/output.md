```python
def p(grid):
    if not grid:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    
    col_lengths = []
    for c in range(cols):
        count = sum(1 for r in range(rows) if grid[r][c] == 5)
        if count > 0:
            col_lengths.append((c, count))
    
    sorted_cols = sorted(col_lengths, key=lambda x: -x[1])
    
    color_map = {}
    for i, (c, _) in enumerate(sorted_cols):
        color_map[c] = i + 1
    
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if grid[r][c] == 5:
                row.append(color_map[c])
            else:
                row.append(grid[r][c])
        output.append(row)
    return output
```