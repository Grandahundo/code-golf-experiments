```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    # Find all non-zero digits present in the grid
    digits = set(v for row in grid for v in row if v != 0)
    
    # Initialize output grid with zeros
    output = [[0] * cols for _ in range(rows)]
    
    for d in digits:
        # Determine the maximum column for this digit
        max_c = -1
        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == d and c > max_c:
                    max_c = c
        if max_c == -1:
            continue  # should not happen, but safe
        
        # Process each row independently
        for r in range(rows):
            # Collect columns where this digit appears in the current row
            cols_with_d = [c for c in range(cols) if grid[r][c] == d]
            if not cols_with_d:
                continue
            
            # Sort ascending; we will process from rightmost to leftmost
            cols_with_d.sort()
            final_cols = set()
            # Process from right to left
            for c in reversed(cols_with_d):
                # Try to move right by 1
                if c + 1 <= max_c and (c + 1) not in final_cols:
                    final_cols.add(c + 1)
                else:
                    final_cols.add(c)
            # Place the digit in the output row
            for c in final_cols:
                output[r][c] = d
                
    return output
```