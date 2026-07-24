def p(grid):
    R = len(grid)
    C = len(grid[0])
    
    # 1. Find all 8-connected components of non-zero cells
    visited = [[False] * C for _ in range(R)]
    components = []
    for i in range(R):
        for j in range(C):
            if grid[i][j] != 0 and not visited[i][j]:
                digit = grid[i][j]
                comp_cells = []
                stack = [(i, j)]
                visited[i][j] = True
                while stack:
                    r, c = stack.pop()
                    comp_cells.append((r, c))
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < R and 0 <= nc < C and not visited[nr][nc] and grid[nr][nc] == digit:
                                visited[nr][nc] = True
                                stack.append((nr, nc))
                components.append({
                    'digit': digit,
                    'cells': comp_cells,
                    'size': len(comp_cells)
                })
    
    # 2. The template is the component with the largest number of cells
    template = max(components, key=lambda x: x['size'])
    
    # 3. Extract template pattern
    cells = template['cells']
    tr = min(r for r, c in cells)
    tc = min(c for r, c in cells)
    max_r = max(r for r, c in cells)
    max_c = max(c for r, c in cells)
    template_h = max_r - tr + 1
    template_w = max_c - tc + 1
    step = max(template_h, template_w) + 1   # spacing between stamps
    
    # Relative coordinates of non-zero cells inside the template's bounding box
    pattern_rel = set()
    for r, c in cells:
        pattern_rel.add((r - tr, c - tc))
    rel_max_r = max(dr for dr, dc in pattern_rel)
    rel_max_c = max(dc for dr, dc in pattern_rel)
    
    # 4. Start with an empty grid and stamp the template itself
    out = [[0] * C for _ in range(R)]
    for dr, dc in pattern_rel:
        out[tr + dr][tc + dc] = template['digit']
    
    # 5. Process every other component (seed)
    # Determine maximum search radius for lattice coordinates
    max_a = (R // step) + 2
    max_b = (C // step) + 2
    
    for comp in components:
        if comp is template:
            continue
        digit = comp['digit']
        seed_cells = comp['cells']
        
        # Find the unique lattice coordinate (a, b) that places the template
        # so that all seed cells lie on its non-zero positions.
        found_a = found_b = None
        for a in range(-max_a, max_a + 1):
            for b in range(-max_b, max_b + 1):
                r0 = tr + step * a
                c0 = tc + step * b
                ok = True
                for r, c in seed_cells:
                    if (r - r0, c - c0) not in pattern_rel:
                        ok = False
                        break
                if ok:
                    found_a, found_b = a, b
                    break
            if found_a is not None:
                break
        
        if found_a is None:
            continue   # should not happen with valid inputs
        
        a, b = found_a, found_b
        
        # 6. Stamp the pattern in the direction (a, b) for k = 1, 2, 3, ...
        k = 1
        while True:
            r0 = tr + step * a * k
            c0 = tc + step * b * k
            # Stop when the entire stamp is off the grid
            if r0 + rel_max_r < 0 or r0 > R - 1 or c0 + rel_max_c < 0 or c0 > C - 1:
                break
            for dr, dc in pattern_rel:
                nr, nc = r0 + dr, c0 + dc
                if 0 <= nr < R and 0 <= nc < C:
                    out[nr][nc] = digit
            k += 1
            
    return out
