def p(grid):
    """
    Transforms a 3x3 input grid into a 9x9 output grid.
    The output is a 3x3 grid of 3x3 blocks. For each cell (i, j) in the input,
    if its value is non-zero, the entire input grid is placed in the corresponding block.
    Otherwise, the block remains all zeros.
    """
    # Initialize 9x9 output with zeros
    output = [[0] * 9 for _ in range(9)]
    
    # Iterate over the 3x3 input grid
    for i in range(3):
        for j in range(3):
            # If the input cell is not zero, copy the whole input into the block
            if grid[i][j] != 0:
                for r in range(3):
                    for c in range(3):
                        output[3 * i + r][3 * j + c] = grid[r][c]
    return output
