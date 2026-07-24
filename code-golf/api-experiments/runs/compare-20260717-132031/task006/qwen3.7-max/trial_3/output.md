Looking at the examples, I need to find the transformation rule.

**Observations:**
- Each input is 3×7, with column 3 always being `5` (a separator)
- This splits the grid into a left 3×3 and right 3×3
- The output is 3×3
- Comparing left and right grids: output is `2` where both left and right cells are `1`, otherwise `0` (logical AND × 2)

**Verification with Example 1:**
- Left: `[[1,0,0],[0,1,0],[1,0,0]]`, Right: `[[0,1,0],[1,1,1],[0,0,0]]`
- AND: `[[0,0,0],[0,1,0],[0,0,0]]` → ×2 → `[[0,0,0],[0,2,0],[0,0,0]]` ✓

**Verification with Example 2:**
- Left: `[[1,1,0],[0,0,1],[1,1,0]]`, Right: `[[0,1,0],[1,1,1],[0,1,0]]`
- AND: `[[0,1,0],[0,0,1],[0,1,0]]` → ×2 → `[[0,2,0],[0,0,2],[0,2,0]]` ✓

**Verification with Example 3:**
- Left: `[[0,0,1],[1,1,0],[0,1,1]]`, Right: `[[0,0,0],[1,0,1],[1,0,1]]`
- AND: `[[0,0,0],[1,0,0],[0,0,1]]` → ×2 → `[[0,0,0],[2,0,0],[0,0,2]]` ✓

```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find the separator column (all values equal to 5)
    sep_col = -1
    for j in range(cols):
        if all(grid[i][j] == 5 for i in range(rows)):
            sep_col = j
            break
    
    # Left grid columns: 0 to sep_col-1
    # Right grid columns: sep_col+1 to end
    left_cols = list(range(0, sep_col))
    right_cols = list(range(sep_col + 1, cols))
    
    out_cols = len(left_cols)
    
    output = []
    for i in range(rows):
        row = []
        for j in range(out_cols):
            l = grid[i][left_cols[j]]
            r = grid[i][right_cols[j]]
            if l != 0 and r != 0:
                row.append(2)
            else:
                row.append(0)
        output.append(row)
    
    return output
```