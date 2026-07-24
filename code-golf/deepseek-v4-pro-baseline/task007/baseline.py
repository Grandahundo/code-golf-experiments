def p(grid):
    """Task 007 (diagstripes): Fill all diagonals with repeating colors.
    Diagonal index d = r + c. Colors repeat every 3 diagonals.
    Extract the color mapping from input, then fill all cells.
    """
    H = len(grid)
    W = len(grid[0])

    # Find which color goes with which diagonal mod 3
    color_map = {}
    for r in range(H):
        for c in range(W):
            if grid[r][c] != 0:
                d = (r + c) % 3
                color_map[d] = grid[r][c]

    # If we couldn't determine all 3, try from other examples
    # (in practice all 3 are always in the input)
    if len(color_map) < 3:
        return [row[:] for row in grid]

    output = [[0] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            d = (r + c) % 3
            output[r][c] = color_map[d]

    return output
