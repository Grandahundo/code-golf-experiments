def p(grid):
    # Helper: replace 1 with 2
    def transform_row(row):
        return [2 if x == 1 else x for x in row]
    
    R = len(grid)
    if R == 0:
        return []
    C = len(grid[0])
    
    # Transform all rows of the input
    transformed = [transform_row(row) for row in grid]
    
    # Find the minimal period T of the row sequence
    T = R  # fallback to full input as pattern
    for t in range(1, R):
        ok = True
        for i in range(R - t):
            if transformed[i] != transformed[i + t]:
                ok = False
                break
        if ok:
            T = t
            break
    
    # Base pattern of length T (transformed)
    pattern = transformed[:T]
    
    # Output height: input height + half of it (floor division)
    L = R + R // 2
    
    # Build output by repeating the pattern
    output = [pattern[i % T] for i in range(L)]
    return output
