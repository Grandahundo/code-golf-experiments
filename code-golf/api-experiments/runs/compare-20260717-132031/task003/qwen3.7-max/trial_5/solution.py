def p(grid):
    n = len(grid)
    
    # Find the smallest period of the row sequence
    period = n
    for p_len in range(1, n + 1):
        match = True
        for i in range(n):
            if grid[i] != grid[i % p_len]:
                match = False
                break
        if match:
            period = p_len
            break
    
    # Output has n + n//2 rows (6 -> 9)
    out_n = n + n // 2
    
    result = []
    for i in range(out_n):
        row = grid[i % period]
        new_row = [2 if x == 1 else x for x in row]
        result.append(new_row)
    
    return result
