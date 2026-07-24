Looking at the examples, I need to find the pattern that transforms a 3×3 input into a 9×9 output.

**Analysis:** The output is a 3×3 grid of 3×3 blocks. Block at position (i, j) in this macro-grid is:
- A copy of the **input grid** if `input[i][j] != 0`
- A **3×3 block of zeros** if `input[i][j] == 0`

Let me verify with Example 2: `input[0][0]=4` (nonzero) → top-left block is the input grid. `input[0][1]=0` → top-middle block is all zeros. This matches perfectly across all examples.

```python
def p(grid):
    n = len(grid)
    result = []
    for i in range(n):
        for r in range(n):
            row = []
            for j in range(n):
                if grid[i][j] != 0:
                    row.extend(grid[r])
                else:
                    row.extend([0] * n)
            result.append(row)
    return result
```