def p(input_grid):
    n = len(input_grid)
    m = len(input_grid[0])
    
    out_n = n * n
    out_m = m * m
    
    output = [[0] * out_m for _ in range(out_n)]
    
    for i in range(n):
        for j in range(m):
            if input_grid[i][j] != 0:
                for ii in range(n):
                    for jj in range(m):
                        output[i * n + ii][j * m + jj] = input_grid[ii][jj]
    
    return output