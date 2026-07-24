def p(grid):
    n = len(grid)
    # Find the smallest period of the row sequence
    period = n
    for p_len in range(1, n + 1):
        if all(grid[i] == grid[i % p_len] for i in range(n)):
            period = p_len
            break
    
    # Generate 9 rows by extending the periodic pattern, doubling all values
    result = []
    for i in range(9):
        row = grid[i % period]
        result.append([x * 2 for x in row])
    
    return result
