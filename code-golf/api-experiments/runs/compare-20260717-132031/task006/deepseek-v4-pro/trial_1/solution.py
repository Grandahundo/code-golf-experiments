def p(grid):
    """
    Transforms an input grid by splitting it into two halves using a column of 5s as a separator.
    Returns a new grid where each cell is 2 if the corresponding cells in both halves are 1, else 0.
    """
    # Find the column index where all elements are 5
    height = len(grid)
    if height == 0:
        return []
    width = len(grid[0])
    sep_col = None
    for c in range(width):
        if all(grid[r][c] == 5 for r in range(height)):
            sep_col = c
            break
    if sep_col is None:
        raise ValueError("No separator column of 5s found")
    
    # Split the grid into left and right halves
    left = [row[:sep_col] for row in grid]
    right = [row[sep_col+1:] for row in grid]
    
    # Compute output using element-wise logical AND (1 AND 1 -> 2, else 0)
    output = [
        [2 if l == 1 and r == 1 else 0 for l, r in zip(left_row, right_row)]
        for left_row, right_row in zip(left, right)
    ]
    return output
