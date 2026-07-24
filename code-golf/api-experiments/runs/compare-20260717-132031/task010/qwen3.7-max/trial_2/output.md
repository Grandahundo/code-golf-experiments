Looking at the examples, I need to figure out the transformation rule:

**Example 1:** Columns with 5s appear at columns 5, 1, 3, 7. Their first (topmost) 5 appears at rows 0, 1, 3, 6 respectively. They get labels 1, 2, 3, 4.

**Example 2:** Columns with 5s appear at columns 7, 3, 5, 1. Their first 5 appears at rows 1, 4, 5, 7 respectively. They get labels 1, 2, 3, 4.

**Rule:** Find all columns containing the value 5. Rank these columns by the row index of their first (topmost) occurrence of 5. The column with the earliest first-5 gets label 1, the next gets 2, etc. Replace all 5s with their column's label.

```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find columns with 5s and the row of their first occurrence
    col_first = {}
    for c in range(cols):
        for r in range(rows):
            if grid[r][c] == 5:
                col_first[c] = r
                break
    
    # Sort columns by first row of 5, then by column index as tiebreaker
    sorted_cols = sorted(col_first.keys(), key=lambda c: (col_first[c], c))
    
    # Assign labels 1, 2, 3, ...
    labels = {}
    for i, c in enumerate(sorted_cols):
        labels[c] = i + 1
    
    # Build output grid: replace 5 with label, keep everything else
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if grid[r][c] == 5:
                row.append(labels[c])
            else:
                row.append(grid[r][c])
        output.append(row)
    
    return output
```