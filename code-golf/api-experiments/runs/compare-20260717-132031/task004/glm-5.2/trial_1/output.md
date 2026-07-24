Looking at the examples, I need to figure out the transformation rule.

**Analysis of Example 1 (6-shape):**
- Input cells in row 1: cols 1,2,3 → Output: cols 2,3,4 (shifted right by 1)
- Row 2: cols 1,4 → cols 2,5 (shifted right by 1)
- Row 3: cols 2,5 → cols 3,6 (shifted right by 1)
- Row 4: cols 3,6 → cols 4,6 (col 3 shifted, col 6 stayed)
- Row 5 (bottom): cols 4,5,6 → cols 4,5,6 (unchanged)

**Pattern:** Each shape (connected component) shifts right by 1, EXCEPT cells in the **bottom row** of the shape's bounding box and cells in the **rightmost column** of the shape's bounding box — those stay pinned.

**Verification with 2-shape and Example 2's 8-shape:** Both confirm this rule. The bottom row and rightmost column cells are anchored; everything else shifts right by 1.

I'll use 8-connectivity (same color) to find connected components, since diagonal connections exist in these shapes.

```python
def p(grid):
    if not grid or not grid[0]:
        return grid
    rows = len(grid)
    cols = len(grid[0])
    
    visited = [[False]*cols for _ in range(rows)]
    components = []
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0 and not visited[r][c]:
                color = grid[r][c]
                stack = [(r, c)]
                visited[r][c] = True
                comp = []
                while stack:
                    cr, cc = stack.pop()
                    comp.append((cr, cc))
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = cr + dr, cc + dc
                            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc] and grid[nr][nc] == color:
                                visited[nr][nc] = True
                                stack.append((nr, nc))
                components.append((color, comp))
    
    output = [[0]*cols for _ in range(rows)]
    
    for color, comp in components:
        max_r = max(cr for cr, cc in comp)
        max_c = max(cc for cr, cc in comp)
        for cr, cc in comp:
            if cr == max_r or cc == max_c:
                output[cr][cc] = color
            else:
                nc = cc + 1
                if nc < cols:
                    output[cr][nc] = color
                else:
                    output[cr][cc] = color
    
    return output
```