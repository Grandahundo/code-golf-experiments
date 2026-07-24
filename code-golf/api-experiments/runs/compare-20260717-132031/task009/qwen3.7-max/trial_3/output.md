```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    # Find border value: first row that is entirely one non-zero value
    border_val = None
    for r in range(rows):
        val = grid[r][0]
        if val != 0 and all(grid[r][c] == val for c in range(cols)):
            border_val = val
            break
    
    # Find border rows and columns
    border_rows = set()
    for r in range(rows):
        if all(grid[r][c] == border_val for c in range(cols)):
            border_rows.add(r)
    
    border_cols = set()
    for c in range(cols):
        if all(grid[r][c] == border_val for r in range(rows)):
            border_cols.add(c)
    
    # Group consecutive non-border rows into cell rows
    cell_row_groups = []
    current_group = []
    for r in range(rows):
        if r not in border_rows:
            current_group.append(r)
        else:
            if current_group:
                cell_row_groups.append(current_group)
                current_group = []
    if current_group:
        cell_row_groups.append(current_group)
    
    # Group consecutive non-border columns into cell columns
    cell_col_groups = []
    current_group = []
    for c in range(cols):
        if c not in border_cols:
            current_group.append(c)
        else:
            if current_group:
                cell_col_groups.append(current_group)
                current_group = []
    if current_group:
        cell_col_groups.append(current_group)
    
    num_cr = len(cell_row_groups)
    num_cc = len(cell_col_groups)
    
    # Extract cell values (top-left pixel of each cell)
    cells = [[0] * num_cc for _ in range(num_cr)]
    for i in range(num_cr):
        for j in range(num_cc):
            cells[i][j] = grid[cell_row_groups[i][0]][cell_col_groups[j][0]]
    
    # Result starts as copy of original cells
    result = [row[:] for row in cells]
    
    # Horizontal fills: for each row, fill between min and max column of each value
    for i in range(num_cr):
        val_pos = {}
        for j in range(num_cc):
            v = cells[i][j]
            if v != 0:
                val_pos.setdefault(v, []).append(j)
        for v, pos in val_pos.items():
            if len(pos) >= 2:
                for j in range(min(pos), max(pos) + 1):
                    result[i][j] = v
    
    # Vertical fills: for each column, fill between min and max row of each value
    for j in range(num_cc):
        val_pos = {}
        for i in range(num_cr):
            v = cells[i][j]
            if v != 0:
                val_pos.setdefault(v, []).append(i)
        for v, pos in val_pos.items():
            if len(pos) >= 2:
                for i in range(min(pos), max(pos) + 1):
                    result[i][j] = v
    
    # Build output grid
    output = [row[:] for row in grid]
    for i in range(num_cr):
        for j in range(num_cc):
            v = result[i][j]
            for r in cell_row_groups[i]:
                for c in cell_col_groups[j]:
                    output[r][c] = v
    
    return output
```