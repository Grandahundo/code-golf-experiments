Looking at the examples, I need to find the pattern:

**Example 1:** Non-zero values are {2, 8, 3}. Checking `(i+j) % 3` for each non-zero cell: `(0+0)%3=0→2`, `(0+1)%3=1→8`, `(0+2)%3=2→3`. Output fills the entire grid using `output[i][j] = mapping[(i+j) % 3]`.

**Example 2:** Non-zero values are {1, 2, 4}. `(2+6)%3=2→1`, `(3+6)%3=0→2`, `(4+6)%3=1→4`. Same rule applies.

**Example 3:** Non-zero values are {8, 3, 4}. `(0+4)%3=1→8`, `(0+5)%3=2→3`, `(3+6)%3=0→4`. Same rule applies.

**General rule:** The period equals the number of distinct non-zero values. Each non-zero value at `(i, j)` maps residue `(i+j) % period` to that value. The output fills every cell using this mapping.

```python
def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    distinct_values = set()
    cells = []
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] != 0:
                distinct_values.add(grid[i][j])
                cells.append((i, j, grid[i][j]))

    period = len(distinct_values)

    if period == 0:
        return [[0] * cols for _ in range(rows)]

    mapping = {}
    for i, j, v in cells:
        r = (i + j) % period
        mapping[r] = v

    output = []
    for i in range(rows):
        row = []
        for j in range(cols):
            r = (i + j) % period
            row.append(mapping.get(r, 0))
        output.append(row)

    return output
```