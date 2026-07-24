Looking at the examples, I need to identify the transformation rule:

1. Each input grid has a column of 5s acting as a separator (column index 3 in these examples)
2. The grid splits into a left half and right half around this separator
3. The output is element-wise: `2` where both left and right are `1`, otherwise `0` (i.e., logical AND multiplied by 2)

Let me verify with Example 1:
- Left: `[[1,0,0],[0,1,0],[1,0,0]]`, Right: `[[0,1,0],[1,1,1],[0,0,0]]`
- AND: only position (1,1) has both=1 → output `[[0,0,0],[0,2,0],[0,0,0]]` ✓

Example 2:
- Left: `[[1,1,0],[0,0,1],[1,1,0]]`, Right: `[[0,1,0],[1,1,1],[0,1,0]]`
- Both=1 at (0,1), (1,2), (2,1) → `[[0,2,0],[0,0,2],[0,2,0]]` ✓

Example 3:
- Left: `[[0,0,1],[1,1,0],[0,1,1]]`, Right: `[[0,0,0],[1,0,1],[1,0,1]]`
- Both=1 at (1,0), (2,2) → `[[0,0,0],[2,0,0],[0,0,2]]` ✓

```python
def p(g):s=g[0].index(5);return[[r[c]*r[c+s+1]*2 for c in range(s)]for r in g]
```