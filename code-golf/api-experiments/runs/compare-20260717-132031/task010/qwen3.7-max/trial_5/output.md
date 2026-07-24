Looking at the examples, I need to identify the transformation rule:

**Example 1 analysis:**
- Column 5 has 5s starting at row 0 → labeled 1
- Column 1 has 5s starting at row 1 → labeled 2
- Column 3 has 5s starting at row 3 → labeled 3
- Column 7 has 5s starting at row 6 → labeled 4

**Example 2 analysis:**
- Column 7 has 5s starting at row 1 → labeled 1
- Column 3 has 5s starting at row 4 → labeled 2
- Column 5 has 5s starting at row 5 → labeled 3
- Column 1 has 5s starting at row 7 → labeled 4

**Rule:** Find all columns containing the value 5. Sort these columns by the row index of their topmost 5 (ascending). Assign labels 1, 2, 3, ... in that order. Replace every 5 with its column's label.

```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find columns with 5s and their topmost row
    col_info = []
    for c in range(cols):
        for r in range(rows):
            if grid[r][c] == 5:
                col_info.append((r, c))
                break
    
    # Sort by topmost row of 5
    col_info.sort()
    
    # Create label mapping: column -> label
    label_map = {}
    for i, (r, c) in enumerate(col_info):
        label_map[c] = i + 1
    
    # Create output grid replacing 5s with labels
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if grid[r][c] == 5:
                row.append(label_map[c])
            else:
                row.append(grid[r][c])
        output.append(row)
    
    return output
```