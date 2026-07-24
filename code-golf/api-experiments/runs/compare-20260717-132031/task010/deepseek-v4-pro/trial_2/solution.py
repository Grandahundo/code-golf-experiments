def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    # Find columns with any 5 and compute their heights.
    col_heights = []
    for c in range(cols):
        height = 0
        for r in range(rows):
            if grid[r][c] == 5:
                height += 1
        if height > 0:
            col_heights.append((height, c))
    # Sort: tallest first; if tie, leftmost column first.
    col_heights.sort(key=lambda x: (-x[0], x[1]))
    # Assign ranks starting from 1.
    rank = 1
    output = [[0] * cols for _ in range(rows)]
    for _, c in col_heights:
        for r in range(rows):
            if grid[r][c] == 5:
                output[r][c] = rank
        rank += 1
    return output
