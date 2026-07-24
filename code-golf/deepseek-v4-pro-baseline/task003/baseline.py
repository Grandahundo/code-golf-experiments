def p(grid):
    """Task 003 (beanstalk): Extend repeating blue (1) pattern as red (2)."""
    H = len(grid)
    W = len(grid[0])
    out_H = 9

    blues = [(r, c) for r in range(H) for c in range(W) if grid[r][c] == 1]
    if not blues:
        return [[0] * W for _ in range(out_H)]

    min_r = min(r for r, _ in blues)

    def get_block(start, s):
        """Return set of (rel_row, rel_col) for block starting at 'start' with step 's'."""
        return set((r - start, c) for r, c in blues if start <= r < start + s)

    def flip_block(block):
        return set((dr, W - 1 - dc) for dr, dc in block)

    # Try step=2 or step=3: pick the one where block0 matches block1
    step = 2
    flip = 0
    for s in (2, 3):
        b0 = get_block(min_r, s)
        b1 = get_block(min_r + s, s)
        if not b1:
            continue
        if b0 == b1:
            step, flip = s, 0
            break
        if b0 == flip_block(b1):
            step, flip = s, 1
            break
    else:
        # Fallback: try step=2 with flip
        step = 2

    pattern = list(get_block(min_r, step))

    output = [[0] * W for _ in range(out_H)]
    flipped = 0
    for offset in range(0, out_H, step):
        for dr, dc in pattern:
            r = offset + dr
            c = dc if flipped == 0 else W - 1 - dc
            if r < out_H:
                output[r][c] = 2
        if flip:
            flipped = 1 - flipped

    return output
