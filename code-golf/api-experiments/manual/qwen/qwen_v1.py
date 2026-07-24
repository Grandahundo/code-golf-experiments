def p(input_grid):
    n = len(input_grid)
    output_size = n * n
    # Initialize output with zeros
    output = [[0] * output_size for _ in range(output_size)]
    
    # For each non-zero cell in input, place the entire input grid
    for i in range(n):
        for j in range(n):
            if input_grid[i][j] != 0:
                # Place the input grid at position (i*n, j*n) in output
                for di in range(n):
                    for dj in range(n):
                        output[i * n + di][j * n + dj] = input_grid[di][dj]
    
    return output