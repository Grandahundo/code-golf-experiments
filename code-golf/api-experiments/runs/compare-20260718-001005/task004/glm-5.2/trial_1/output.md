Looking at the examples, I need to identify the transformation rule:

1. Each colored shape shifts right by 1 column
2. But cells are blocked from moving past the rightmost extent of their color's shape
3. Within a row, cells process right-to-left (traffic jam style) - a cell moves right only if the target position is empty

For each color, I track the maximum column (rightmost extent). Then processing right-to-left within each row, a cell at column `j` shifts to `j+1` if `j < max_col` and the position to its right is still empty.

Verifying with Example 1:
- Color 6: max col = 6. Row 5 (cells at 4,5,6): cell at 6 stays (6<6 is false), cells at 5,4 blocked by occupied cells → stays. ✓
- Row 4 (cells at 3,6): cell at 6 stays, cell at 3 shifts to 4 (empty). ✓

Verifying with Example 2:
- Color 8: max col = 8. Row 4 (cells at 3,8): cell at 8 stays, cell at 3 shifts to 4. ✓
- Row 5 (cells at 4-8): cell at 8 stays, rest blocked. ✓

```python
def p(g):
 C=len(g[0]);m=[0]*10
 for r in g:
  for j,c in enumerate(r):m[c]=max(m[c],j)
 for r in g:
  for j in range(C)[::-1]:
   if r[j]and j<m[r[j]]and r[j+1]<1:r[j],r[j+1]=0,r[j]
 return g
```