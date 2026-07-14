def p(grid):
    """Task 002 (honeypots): Fill enclosed black regions with yellow (4).
    Green (3) borders define boxes. Any black (0) cell that cannot
    reach the grid edge via black cells becomes yellow.
    """
    H = len(grid)
    W = len(grid[0])
    output = [row[:] for row in grid]
    seen = [[False] * W for _ in range(H)]

    # Flood fill from edge black cells
    stack = []
    for r in range(H):
        if output[r][0] == 0: stack.append((r, 0))
        if output[r][W - 1] == 0: stack.append((r, W - 1))
    for c in range(W):
        if output[0][c] == 0: stack.append((0, c))
        if output[H - 1][c] == 0: stack.append((H - 1, c))

    while stack:
        r, c = stack.pop()
        if r < 0 or r >= H or c < 0 or c >= W:
            continue
        if seen[r][c] or output[r][c] != 0:
            continue
        seen[r][c] = True
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            stack.append((r + dr, c + dc))

    # Enclosed black → yellow
    for r in range(H):
        for c in range(W):
            if output[r][c] == 0 and not seen[r][c]:
                output[r][c] = 4

    return output
