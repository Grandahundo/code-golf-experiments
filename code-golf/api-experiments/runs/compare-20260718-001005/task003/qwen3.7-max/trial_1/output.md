Looking at the examples, I need to find the transformation rule:

1. **Input 6×3 → Output 9×3**: The output has 1.5× the rows of the input.
2. **Values**: 1s become 2s, 0s stay 0.
3. **Pattern**: The rows repeat with some fundamental period. I need to find the shortest row period `q` such that `g[i] == g[i%q]` for all rows, then extend that pattern to `len(g)*3//2` rows.

**Verifying the period-finding:**
- Example 1: period=4 (rows 0-3 repeat), extended to 9 rows
- Example 2: period=2 (rows 0-1 repeat), extended to 9 rows  
- Example 3: period=3 (rows 0-2 repeat), extended to 9 rows

**Key insight for period detection:** `g[q:] == g[:-q]` checks if shifting by `q` gives matching elements, which is equivalent to checking period `q`.

```python
def p(g):
 q=1
 while g[q:]!=g[:-q]:q+=1
 return[[v+(v==1)for v in g[r%q]]for r in range(len(g)*3//2)]
```