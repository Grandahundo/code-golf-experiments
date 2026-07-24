def p(grid):
    H = len(grid)
    W = len(grid[0])
    
    # Collect values for each anti-diagonal (r + c)
    diag_val = {}
    for r in range(H):
        for c in range(W):
            v = grid[r][c]
            if v != 0:
                d = r + c
                diag_val[d] = v  # assume all entries on the same d have the same value
                
    if not diag_val:
        # No pattern found: return copy of input (all zeros)
        return [row[:] for row in grid]
    
    # Base sequence from anti-diagonals in increasing order
    sorted_d = sorted(diag_val.keys())
    seq = [diag_val[d] for d in sorted_d]
    L = len(seq)
    min_d = sorted_d[0]
    shift = min_d % L
    
    # Right-rotate the sequence by 'shift' places
    if shift:
        tiling = seq[-shift:] + seq[:-shift]
    else:
        tiling = seq
        
    # Fill the output grid using the tiling sequence based on (r + c) % L
    output = [[0] * W for _ in range(H)]
    for r in range(H):
        for c in range(W):
            idx = (r + c) % L
            output[r][c] = tiling[idx]
            
    return output
