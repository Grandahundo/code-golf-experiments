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
