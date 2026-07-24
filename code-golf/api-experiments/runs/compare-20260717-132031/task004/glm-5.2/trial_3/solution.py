def p(grid):
    if not grid or not grid[0]:
        return []
    R = len(grid)
    C = len(grid[0])
    out = [[0] * C for _ in range(R)]
    visited = [[False] * C for _ in range(R)]
    
    for i in range(R):
        for j in range(C):
            if grid[i][j] != 0 and not visited[i][j]:
                color = grid[i][j]
                # Find the 4-connected component of this color
                stack = [(i, j)]
                visited[i][j] = True
                comp = []
                while stack:
                    r, c = stack.pop()
                    comp.append((r, c))
                    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < R and 0 <= nc < C:
                            if not visited[nr][nc] and grid[nr][nc] == color:
                                visited[nr][nc] = True
                                stack.append((nr, nc))
                # Bottom row and rightmost column of this component
                max_r = max(r for r, c in comp)
                max_c = max(c for r, c in comp)
                # Transform: cells on the bottom row or rightmost column stay;
                # all others shift right by 1
                for r, c in comp:
                    if r == max_r or c == max_c:
                        out[r][c] = color
                    else:
                        out[r][c + 1] = color
    return out
