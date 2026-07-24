```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    # Find all maximal contiguous vertical segments of 5s
    segments = []  # (length, col, start_row, end_row)
    for c in range(cols):
        r = 0
        while r < rows:
            if grid[r][c] == 5:
                start = r
                while r < rows and grid[r][c] == 5:
                    r += 1
                end = r - 1
                length = end - start + 1
                segments.append((length, c, start, end))
            else:
                r += 1
    # Sort segments: primary by length descending, secondary by column ascending for determinism
    segments.sort(key=lambda x: (-x[0], x[1]))
    # Build output grid, initially all zero
    output = [[0] * cols for _ in range(rows)]
    for idx, (length, c, start, end) in enumerate(segments):
        num = idx + 1  # assign 1, 2, 3, ...
        for r in range(start, end + 1):
            output[r][c] = num
    return output
```