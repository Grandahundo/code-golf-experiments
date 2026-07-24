def p(grid):
    rows = len(grid)
    if rows == 0:
        return []
    cols = len(grid[0])

    output = [[0] * cols for _ in range(rows)]

    visited = [[False] * cols for _ in range(rows)]
    components = []

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                val = grid[r][c]
                component = []
                queue = [(r, c)]
                visited[r][c] = True
                while queue:
                    cr, cc = queue.pop(0)
                    component.append((cr, cc, val))
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == val:
                                visited[nr][nc] = True
                                queue.append((nr, nc))
                components.append(component)

    for component in components:
        max_col = max(cc for _, cc, _ in component)

        row_cells = {}
        for r, c, v in component:
            if r not in row_cells:
                row_cells[r] = []
            row_cells[r].append((c, v))

        for r, cells in row_cells.items():
            cells.sort(key=lambda x: x[0], reverse=True)
            placed = set()
            for c, v in cells:
                if c + 1 <= max_col and (c + 1) not in placed:
                    output[r][c + 1] = v
                    placed.add(c + 1)
                else:
                    output[r][c] = v
                    placed.add(c)

    return output
