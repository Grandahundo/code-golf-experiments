```python
def p(grid):
    if not grid or not grid[0]:
        return [[]] if not grid else []
    n_rows = len(grid)
    n_cols = len(grid[0])
    out = [row[:] for row in grid]

    segments = []
    for c in range(n_cols):
        r = 0
        while r < n_rows:
            if grid[r][c] == 5:
                start = r
                while r < n_rows and grid[r][c] == 5:
                    r += 1
                end = r - 1
                segments.append((start, c, end))
            else:
                r += 1

    segments.sort(key=lambda s: (s[0], s[1]))
    for color, (start, c, end) in enumerate(segments, start=1):
        for r in range(start, end + 1):
            out[r][c] = color

    return out
```