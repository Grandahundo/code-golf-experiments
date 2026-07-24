Looking at the examples, I can see:
- Each input grid has a separator column of 5s dividing it into left and right halves
- The output is a grid where cells are 2 if both corresponding cells in the left and right halves are 1, otherwise 0 (logical AND × 2)

Let me verify with Example 1:
- Left: `[[1,0,0],[0,1,0],[1,0,0]]`, Right: `[[0,1,0],[1,1,1],[0,0,0]]`
- AND at (1,1): 1 AND 1 → 2, all others have at least one 0 → 0. Matches output.

```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find the separator column (column where all values are 5)
    sep_col = -1
    for c in range(cols):
        if all(grid[r][c] == 5 for r in range(rows)):
            sep_col = c
            break
    
    right_start = sep_col + 1
    out_cols = sep_col
    
    output = []
    for r in range(rows):
        row = []
        for c in range(out_cols):
            l_val = grid[r][c]
            r_val = grid[r][right_start + c]
            if l_val == 1 and r_val == 1:
                row.append(2)
            else:
                row.append(0)
        output.append(row)
    
    return output
```