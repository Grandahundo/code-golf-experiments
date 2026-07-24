def p(grid):
    """Task 009 (gridlines): Connect same-colored dots with lines.
    Grid has gridlines every 3rd row/col (spacing=2).
    Extract the bitmap, connect same-colored dots sharing rows/cols,
    then re-render with gridlines.
    """
    H = len(grid)
    W = len(grid[0])

    # Gridlines: (row+1) % 3 == 0 or (col+1) % 3 == 0
    # Find the linecolor (color of gridlines)
    def is_gridline(r, c):
        return (r + 1) % 3 == 0 or (c + 1) % 3 == 0

    # Determine linecolor from a gridline cell
    linecolor = None
    for r in range(H):
        for c in range(W):
            if is_gridline(r, c) and grid[r][c] != 0:
                linecolor = grid[r][c]
                break
        if linecolor is not None:
            break

    if linecolor is None:
        return [row[:] for row in grid]

    # Extract bitmap: bitmap[r][c] = color at cell (r*3, c*3) area
    bm_H = (H + 1) // 3
    bm_W = (W + 1) // 3
    bitmap = [[0] * bm_W for _ in range(bm_H)]

    for br in range(bm_H):
        for bc in range(bm_W):
            gr = br * 3
            gc = bc * 3
            # Find non-linecolor, non-zero value in the 2x2 block
            for dr in range(2):
                for dc in range(2):
                    r, c = gr + dr, gc + dc
                    if r < H and c < W:
                        v = grid[r][c]
                        if v != 0 and v != linecolor:
                            bitmap[br][bc] = v

    # Connect same-colored dots that share rows or columns
    bm_out = [row[:] for row in bitmap]

    # For each color, find all dot positions
    dots_by_color = {}
    for br in range(bm_H):
        for bc in range(bm_W):
            color = bitmap[br][bc]
            if color != 0:
                dots_by_color.setdefault(color, []).append((br, bc))

    # Connect dots of the same color
    for color, dots in dots_by_color.items():
        for i in range(len(dots)):
            for j in range(i + 1, len(dots)):
                r1, c1 = dots[i]
                r2, c2 = dots[j]
                if r1 == r2:
                    # Same row: draw horizontal line
                    for cc in range(min(c1, c2), max(c1, c2) + 1):
                        bm_out[r1][cc] = color
                elif c1 == c2:
                    # Same column: draw vertical line
                    for rr in range(min(r1, r2), max(r1, r2) + 1):
                        bm_out[rr][c1] = color

    # Re-render with gridlines
    out_H = bm_H * 3 - 1
    out_W = bm_W * 3 - 1
    output = [[0] * out_W for _ in range(out_H)]

    for r in range(out_H):
        for c in range(out_W):
            if is_gridline(r, c):
                output[r][c] = linecolor

    for br in range(bm_H):
        for bc in range(bm_W):
            color = bm_out[br][bc]
            if color != 0:
                for dr in range(2):
                    for dc in range(2):
                        r, c = br * 3 + dr, bc * 3 + dc
                        if r < out_H and c < out_W:
                            if output[r][c] == 0 or output[r][c] == linecolor:
                                output[r][c] = color

    return output
