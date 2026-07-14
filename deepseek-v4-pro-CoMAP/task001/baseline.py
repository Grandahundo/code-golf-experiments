def p(grid):
    """Task 001 (fractal): Cartesian product scaling.
    Input: SxS grid, output: S^2 x S^2.
    Each input pair (r1,c1),(r2,c2) places the input color
    at output position (r1*S+r2, c1*S+c2).
    """
    size = len(grid)
    pixels = [(r, c, grid[r][c]) for r in range(size) for c in range(size) if grid[r][c]]

    out_size = size * size
    output = [[0] * out_size for _ in range(out_size)]

    for r1, c1, color in pixels:
        for r2, c2, _ in pixels:
            output[r1 * size + r2][c1 * size + c2] = color

    return output
