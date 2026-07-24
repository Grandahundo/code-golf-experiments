def p(grid):
    # Determine dimensions
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    # Collect all distinct non-zero values in the input
    non_zero_vals = set()
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0:
                non_zero_vals.add(grid[i][j])
    k = len(non_zero_vals)
    
    # If no non-zero values, return the input unchanged (or all zeros)
    if k == 0:
        return [row[:] for row in grid]
    
    # Learn the mapping from residue (i+j) % k to the pattern value
    S = [None] * k
    for i in range(rows):
        for j in range(cols):
            v = grid[i][j]
            if v != 0:
                r = (i + j) % k
                if S[r] is None:
                    S[r] = v
                # In a well-formed input, all occurrences of the same residue are consistent
    
    # If some residue is missing (should not happen in the given tasks), 
    # we try to infer it by cycling the known values (fallback).
    # This keeps S fully populated.
    if any(x is None for x in S):
        # Find the first known index and fill by shifting
        first_known = next((i for i, x in enumerate(S) if x is not None), None)
        if first_known is not None:
            # Rotate until all are filled (simple cyclic repetition)
            # This assumes the sequence is just the known values in order.
            # Since the problem guarantees completeness, this is rarely used.
            known_vals = [v for v in S if v is not None]
            if len(known_vals) < k:
                # Extend by repeating the known pattern (heuristic)
                rep = known_vals
                while len(rep) < k:
                    rep += known_vals
                full_seq = rep[:k]
                # Align to the known positions: we need to find offset such that known positions match
                # For simplicity, place at the first known residue - this may not always be correct,
                # but we trust the input provides all residues.
                offset = first_known
                for d in range(k):
                    idx = (offset + d) % k
                    if S[idx] is None:
                        S[idx] = full_seq[d]
    
    # Generate output grid by tiling the pattern
    out = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        for j in range(cols):
            out[i][j] = S[(i + j) % k]
    
    return out
