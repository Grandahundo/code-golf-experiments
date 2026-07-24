```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Count 5s in each column
    counts = {}
    for c in range(cols):
        count = 0
        for r in range(rows):
            if grid[r][c] == 5:
                count += 1
        if count > 0:
            counts[c] = count
    
    # Sort columns by count descending
    sorted_cols = sorted(counts.keys(), key=lambda c: counts[c], reverse=True)
    
    # Assign ranks (1-based)
    rank = {}
    for i, c in enumerate(sorted_cols):
        rank[c] = i + 1
    
    # Build output grid
    output = []
    for r in range(rows):
        row = []
        for c in range(cols):
            if grid[r][c] == 5:
                row.append(rank[c])
            else:
                row.append(0)
        output.append(row)
    
    return output
```