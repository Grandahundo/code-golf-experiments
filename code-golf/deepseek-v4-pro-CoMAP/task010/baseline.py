def p(grid):
    """Task 010 (barchart): Number bars by height (tallest=1, second=2, ...).
    Input has gray (5) bars. Output colors each bar with its rank.
    """
    H = len(grid)
    W = len(grid[0])

    # Find columns that have gray pixels
    bar_cols = []
    for c in range(W):
        for r in range(H):
            if grid[r][c] == 5:
                bar_cols.append(c)
                break

    # For each bar column, measure its height
    bar_heights = []
    for c in bar_cols:
        h = 0
        for r in range(H):
            if grid[r][c] == 5:
                h += 1
        bar_heights.append((c, h))

    # Sort by height descending, then assign ranks (1-indexed)
    bar_heights.sort(key=lambda x: -x[1])
    rank = {}
    for i, (c, h) in enumerate(bar_heights):
        rank[c] = i + 1

    # Build output: replace gray with rank number
    output = [[0] * W for _ in range(H)]
    for c, h in bar_heights:
        rnk = rank[c]
        for r in range(H - h, H):
            output[r][c] = rnk

    return output
