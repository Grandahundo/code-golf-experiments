def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0
    
    visited = set()
    components = []
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and (r, c) not in visited:
                color = grid[r][c]
                component = []
                queue = [(r, c)]
                visited.add((r, c))
                while queue:
                    cr, cc = queue.pop(0)
                    component.append((cr, cc))
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in visited and grid[nr][nc] == color:
                                visited.add((nr, nc))
                                queue.append((nr, nc))
                components.append((color, component))
    
    if not components:
        return [row[:] for row in grid]
    
    components.sort(key=lambda x: len(x[1]), reverse=True)
    template_color, template_cells = components[0]
    
    tr_min = min(r for r, c in template_cells)
    tr_max = max(r for r, c in template_cells)
    tc_min = min(c for r, c in template_cells)
    tc_max = max(c for r, c in template_cells)
    H = tr_max - tr_min + 1
    W = tc_max - tc_min + 1
    
    template_pattern = set()
    for r, c in template_cells:
        template_pattern.add((r - tr_min, c - tc_min))
    
    output = [row[:] for row in grid]
    
    for color, cells in components[1:]:
        found_dir = None
        for dr in [-(H + 1), 0, H + 1]:
            for dc in [-(W + 1), 0, W + 1]:
                if dr == 0 and dc == 0:
                    continue
                copy_r = tr_min + dr
                copy_c = tc_min + dc
                contains_all = True
                for mr, mc in cells:
                    rel_r = mr - copy_r
                    rel_c = mc - copy_c
                    if (rel_r, rel_c) not in template_pattern:
                        contains_all = False
                        break
                if contains_all:
                    found_dir = (dr, dc)
                    break
            if found_dir:
                break
        
        if found_dir:
            dr, dc = found_dir
            k = 1
            while True:
                copy_r = tr_min + k * dr
                copy_c = tc_min + k * dc
                any_in_bounds = False
                for pr, pc in template_pattern:
                    r = copy_r + pr
                    c = copy_c + pc
                    if 0 <= r < rows and 0 <= c < cols:
                        any_in_bounds = True
                        break
                if not any_in_bounds:
                    break
                for pr, pc in template_pattern:
                    r = copy_r + pr
                    c = copy_c + pc
                    if 0 <= r < rows and 0 <= c < cols:
                        output[r][c] = color
                k += 1
    
    return output
