def p(grid):
    if not grid:
        return []
    
    n = len(grid)
    
    # Find smallest period P such that grid[i] == grid[i+P] for all valid i
    P = n
    for p in range(1, n):
        if all(grid[i] == grid[i + p] for i in range(n - p)):
            P = p
            break
    
    # Generate output: extend to n * 3 // 2 rows, multiply values by 2
    out_n = n * 3 // 2
    return [[v * 2 for v in grid[i % P]] for i in range(out_n)]
