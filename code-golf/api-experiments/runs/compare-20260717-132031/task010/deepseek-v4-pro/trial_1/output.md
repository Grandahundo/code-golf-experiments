```python
def p(grid):
    height = len(grid)
    width = len(grid[0])
    runs = []
    # Collect all vertical contiguous runs of 5s
    for col in range(width):
        row = 0
        while row < height:
            if grid[row][col] == 5:
                start = row
                while row < height and grid[row][col] == 5:
                    row += 1
                end = row - 1
                runs.append((start, col, start, end))
            else:
                row += 1
    # Sort runs by topmost row, then by column for tie-breaking
    runs.sort(key=lambda r: (r[0], r[1]))
    # Initialize output grid with zeros
    output = [[0] * width for _ in range(height)]
    # Label each run with increasing integers starting from 1
    for label, (top, col, start, end) in enumerate(runs, start=1):
        for row in range(start, end + 1):
            output[row][col] = label
    return output
```