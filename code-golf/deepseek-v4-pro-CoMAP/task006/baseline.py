def p(grid):
    """Task 006 (intersect): Intersection of left and right halves.
    Input: (2*width+1) x height grid. Gray (5) column at 'width' separates
    left and right halves. Output: width x height. Red (2) where both
    halves have a non-black, non-gray pixel at the same position.
    """
    H = len(grid)
    W = len(grid[0])
    width = W // 2  # 2*width+1 → width = (W-1)//2

    out_W = width
    out_H = H
    output = [[0] * out_W for _ in range(out_H)]

    for r in range(out_H):
        for c in range(out_W):
            left = grid[r][c]
            right = grid[r][c + width + 1]
            if left != 0 and right != 0:
                output[r][c] = 2

    return output
