Looking at the examples, I need to identify the transformation rule:

**Example 1:** Columns with 5s: col 5 (9 fives), col 1 (8 fives), col 3 (6 fives), col 7 (3 fives) → labeled 1, 2, 3, 4 respectively.

**Example 2:** Columns with 5s: col 7 (8 fives), col 3 (5 fives), col 5 (4 fives), col 1 (2 fives) → labeled 1, 2, 3, 4 respectively.

**Rule:** Find all columns containing 5, count the 5s in each, rank by count descending (longest column of 5s gets label 1, next gets 2, etc.), and replace each 5 with its rank label. All other cells become 0.

```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # Count 5s in each column
    col_counts = {}
    for c in range(cols):
        count = 0
        for r in range(rows):
            if grid[r][c] == 5:
                count += 1
        if count > 0:
            col_counts[c] = count

    # Sort columns by count descending, then by column index ascending for ties
    sorted_cols = sorted(col_counts.keys(), key=lambda c: (-col_counts[c], c))

    # Create output grid of zeros
    output = [[0] * cols for _ in range(rows)]

    # Assign labels 1, 2, 3, ... to columns in sorted order
    for label, c in enumerate(sorted_cols, 1):
        for r in range(rows):
            if grid[r][c] == 5:
                output[r][c] = label

    return output
```