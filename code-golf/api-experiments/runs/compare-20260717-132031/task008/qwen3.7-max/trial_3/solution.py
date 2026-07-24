def p(grid):
    rows = len(grid)
    cols = len(grid[0])
    
    cells_2 = []
    cells_8 = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                cells_2.append((r, c))
            elif grid[r][c] == 8:
                cells_8.append((r, c))
    
    if not cells_2 or not cells_8:
        return [row[:] for row in grid]
    
    min_r2 = min(r for r, c in cells_2)
    max_r2 = max(r for r, c in cells_2)
    min_c2 = min(c for r, c in cells_2)
    max_c2 = max(c for r, c in cells_2)
    min_r8 = min(r for r, c in cells_8)
    max_r8 = max(r for r, c in cells_8)
    min_c8 = min(c for r, c in cells_8)
    max_c8 = max(c for r, c in cells_8)
    
    h_overlap = max_c2 >= min_c8 and min_c2 <= max_c8
    v_overlap = max_r2 >= min_r8 and min_r2 <= max_r8
    
    dr, dc = 0, 0
    
    if h_overlap and not v_overlap:
        cols_2 = {}
        for r, c in cells_2:
            cols_2.setdefault(c, []).append(r)
        cols_8 = {}
        for r, c in cells_8:
            cols_8.setdefault(c, []).append(r)
        
        if max_r2 < min_r8:
            min_gap = float('inf')
            for c in cols_2:
                if c in cols_8:
                    gap = min(cols_8[c]) - max(cols_2[c]) - 1
                    if gap < min_gap:
                        min_gap = gap
            if min_gap == float('inf'):
                min_gap = min_r8 - max_r2 - 1
            dr = min_gap
        else:
            min_gap = float('inf')
            for c in cols_2:
                if c in cols_8:
                    gap = min(cols_2[c]) - max(cols_8[c]) - 1
                    if gap < min_gap:
                        min_gap = gap
            if min_gap == float('inf'):
                min_gap = min_r2 - max_r8 - 1
            dr = -min_gap
    elif v_overlap and not h_overlap:
        rows_2 = {}
        for r, c in cells_2:
            rows_2.setdefault(r, []).append(c)
        rows_8 = {}
        for r, c in cells_8:
            rows_8.setdefault(r, []).append(c)
        
        if max_c2 < min_c8:
            min_gap = float('inf')
            for r in rows_2:
                if r in rows_8:
                    gap = min(rows_8[r]) - max(rows_2[r]) - 1
                    if gap < min_gap:
                        min_gap = gap
            if min_gap == float('inf'):
                min_gap = min_c8 - max_c2 - 1
            dc = min_gap
        else:
            min_gap = float('inf')
            for r in rows_2:
                if r in rows_8:
                    gap = min(rows_2[r]) - max(rows_8[r]) - 1
                    if gap < min_gap:
                        min_gap = gap
            if min_gap == float('inf'):
                min_gap = min_c2 - max_c8 - 1
            dc = -min_gap
    
    output = [[0] * cols for _ in range(rows)]
    for r, c in cells_8:
        output[r][c] = 8
    for r, c in cells_2:
        output[r + dr][c + dc] = 2
    
    return output
