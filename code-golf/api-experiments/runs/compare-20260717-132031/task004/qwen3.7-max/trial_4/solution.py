def p(grid):
    if not grid or not grid[0]:
        return grid
    
    rows = len(grid)
    cols = len(grid[0])
    
    # Find 8-connected components of same-color cells
    visited = [[False] * cols for _ in range(rows)]
    components = []
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                v = grid[r][c]
                comp = []
                stack = [(r, c)]
                visited[r][c] = True
                while stack:
                    cr, cc = stack.pop()
                    comp.append((cr, cc))
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == v:
                                visited[nr][nc] = True
                                stack.append((nr, nc))
                components.append((v, comp))
    
    # Determine which cells are "fixed" (don't move)
    fixed = set()
    
    for v, cells in components:
        # Group cells by row
        rows_dict = {}
        for r, c in cells:
            if r not in rows_dict:
                rows_dict[r] = []
            rows_dict[r].append(c)
        
        r_max = max(rows_dict.keys())
        
        # Bottom row of component is fixed
        for c in rows_dict[r_max]:
            fixed.add((r_max, c))
        
        # Propagate fixed status upward: a cell is fixed if the cell
        # directly below it (same column) is also fixed
        for r in range(r_max - 1, -1, -1):
            if r in rows_dict:
                for c in rows_dict[r]:
                    if (r + 1, c) in fixed:
                        fixed.add((r, c))
    
    # Build output grid: fixed cells stay, others shift right by 1
    output = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            v = grid[r][c]
            if v == 0:
                continue
            if (r, c) in fixed:
                output[r][c] = v
            else:
                nc = c + 1
                if nc < cols:
                    output[r][nc] = v
                else:
                    output[r][c] = v
    
    return output
