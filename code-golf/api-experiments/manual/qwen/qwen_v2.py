def p(input_grid):
    n = len(input_grid)
    output_size = 3 * n
    output = [[0] * output_size for _ in range(output_size)]
    
    for i in range(n):
        for j in range(n):
            if input_grid[i][j] != 0:
                for di in range(n):
                    for dj in range(n):
                        output[3*i + di][3*j + dj] = input_grid[di][dj]
    
    return output