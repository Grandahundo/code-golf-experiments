```python
from collections import defaultdict

def p(grid):
    h = len(grid)
    w = len(grid[0])
    
    # Identify the grid-line number G (appears in full rows)
    G = None
    for row in grid:
        if all(x == row[0] for x in row) and row[0] != 0:
            G = row[0]
            break
    if G is None:          # no grid lines (unlikely per examples)
        return grid
    
    # Find rows and columns that are completely G
    H = [i for i in range(h) if all(grid[i][j] == G for j in range(w))]
    V = [j for j in range(w) if all(grid[i][j] == G for i in range(h))]
    H_set = set(H)
    V_set = set(V)
    
    # Partition rows and columns into cell intervals (blocks between lines)
    row_ints = []
    prev = 0
    for r in sorted(H):
        if prev < r:
            row_ints.append((prev, r))
        prev = r + 1
    if prev < h:
        row_ints.append((prev, h))
    
    col_ints = []
    prev = 0
    for c in sorted(V):
        if prev < c:
            col_ints.append((prev, c))
        prev = c + 1
    if prev < w:
        col_ints.append((prev, w))
    
    R = len(row_ints)
    C = len(col_ints)
    
    # Extract the value inside each cell (blocks are uniform)
    cells = [[0] * C for _ in range(R)]
    orig = defaultdict(list)
    for i in range(R):
        rs, re = row_ints[i]
        for j in range(C):
            cs, ce = col_ints[j]
            val = grid[rs][cs]
            if val != 0 and val != G:
                cells[i][j] = val
                orig[val].append((i, j))
    
    # Apply horizontal and vertical filling based on original positions only
    new_cells = [r[:] for r in cells]
    for N, pos_list in orig.items():
        # Horizontal fill
        row_g = defaultdict(list)
        for r, c in pos_list:
            row_g[r].append(c)
        for r, cols in row_g.items():
            if len(cols) >= 2:
                mn, mx = min(cols), max(cols)
                for c in range(mn, mx + 1):
                    new_cells[r][c] = N
        
        # Vertical fill
        col_g = defaultdict(list)
        for r, c in pos_list:
            col_g[c].append(r)
        for c, rows in col_g.items():
            if len(rows) >= 2:
                mn, mx = min(rows), max(rows)
                for r in range(mn, mx + 1):
                    new_cells[r][c] = N
    
    # Build output grid preserving the grid lines
    out = [[0] * w for _ in range(h)]
    for i in range(h):
        for j in range(w):
            if i in H_set or j in V_set:
                out[i][j] = G
    
    # Place the filled cell values into the corresponding 2D blocks
    for i in range(R):
        rs, re = row_ints[i]
        for j in range(C):
            cs, ce = col_ints[j]
            fill = new_cells[i][j]
            for x in range(rs, re):
                for y in range(cs, ce):
                    out[x][y] = fill
    
    return out
```