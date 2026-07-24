```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    mapping = {}
    counter = 1
    
    # Determine column labels based on first appearance order
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0 and j not in mapping:
                mapping[j] = counter
                counter += 1
    
    # Build output grid
    output = []
    for i in range(rows):
        row = []
        for j in range(cols):
            if grid[i][j] != 0:
                row.append(mapping[j])
            else:
                row.append(0)
        output.append(row)
    
    return output
```