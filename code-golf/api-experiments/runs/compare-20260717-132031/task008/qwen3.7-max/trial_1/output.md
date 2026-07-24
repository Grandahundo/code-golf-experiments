Looking at the examples, I need to identify the transformation rule:

1. **Example 1**: The 2-shape (rows 2-3) moves **down** by 6 rows to sit just above the 8-shape (rows 10-11). They overlap in columns.
2. **Example 2**: The 2-shape (cols 0-2) moves **right** by 3 columns to sit just left of the 8-shape (cols 6-7). They overlap in rows.
3. **Example 3**: The 2-shape (rows 6-8) moves **up** by 3 rows to sit just below the 8-shape (rows 1-2). They overlap in columns.

**Rule**: The smaller-valued shape slides toward the larger-valued shape along the axis where their bounding boxes don't overlap, stopping at the maximum displacement that avoids cell-to-cell collision.

```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    shapes = {}
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v != 0:
                if v not in shapes:
                    shapes[v] = []
                shapes[v].append((r, c))
    
    if len(shapes) < 2:
        return [row[:] for row in grid]
    
    values = sorted(shapes.keys())
    moving_val = values[0]
    stationary_val = values[-1]
    
    moving_cells = shapes[moving_val]
    stationary_cells = shapes[stationary_val]
    
    min_r_m = min(r for r, c in moving_cells)
    max_r_m = max(r for r, c in moving_cells)
    min_c_m = min(c for r, c in moving_cells)
    max_c_m = max(c for r, c in moving_cells)
    
    min_r_s = min(r for r, c in stationary_cells)
    max_r_s = max(r for r, c in stationary_cells)
    min_c_s = min(c for r, c in stationary_cells)
    max_c_s = max(c for r, c in stationary_cells)
    
    row_overlap = max(min_r_m, min_r_s) <= min(max_r_m, max_r_s)
    col_overlap = max(min_c_m, min_c_s) <= min(max_c_m, max_c_s)
    
    dr, dc = 0, 0
    
    if not row_overlap and col_overlap:
        dr = 1 if max_r_m < min_r_s else -1
    elif row_overlap and not col_overlap:
        dc = 1 if max_c_m < min_c_s else -1
    elif not row_overlap and not col_overlap:
        row_gap = min_r_s - max_r_m if max_r_m < min_r_s else min_r_m - max_r_s
        col_gap = min_c_s - max_c_m if max_c_m < min_c_s else min_c_m - max_c_s
        if row_gap <= col_gap:
            dr = 1 if max_r_m < min_r_s else -1
        else:
            dc = 1 if max_c_m < min_c_s else -1
    else:
        return [row[:] for row in grid]
    
    max_d = float('inf')
    
    if dr > 0:
        max_d = rows - 1 - max_r_m
        for r_m, c_m in moving_cells:
            for r_s, c_s in stationary_cells:
                if c_m == c_s and r_s > r_m:
                    max_d = min(max_d, r_s - r_m - 1)
    elif dr < 0:
        max_d = min_r_m
        for r_m, c_m in moving_cells:
            for r_s, c_s in stationary_cells:
                if c_m == c_s and r_s < r_m:
                    max_d = min(max_d, r_m - r_s - 1)
    elif dc > 0:
        max_d = cols - 1 - max_c_m
        for r_m, c_m in moving_cells:
            for r_s, c_s in stationary_cells:
                if r_m == r_s and c_s > c_m:
                    max_d = min(max_d, c_s - c_m - 1)
    elif dc < 0:
        max_d = min_c_m
        for r_m, c_m in moving_cells:
            for r_s, c_s in stationary_cells:
                if r_m == r_s and c_s < c_m:
                    max_d = min(max_d, c_m - c_s - 1)
    
    output = [[0] * cols for _ in range(rows)]
    
    for r, c in stationary_cells:
        output[r][c] = stationary_val
    
    for r, c in moving_cells:
        output[r + dr * max_d][c + dc * max_d] = moving_val
    
    for v in values[1:-1]:
        for r, c in shapes[v]:
            output[r][c] = v
    
    return output
```