Looking at the examples, I need to find the pattern:

**Analysis:**
- Each 3×3 input produces a 9×9 output
- The output is a 3×3 grid of 3×3 blocks
- Block at position (r,c) = the input pattern itself if input[r][c] ≠ 0, else all zeros

This means: `output[R][C] = input[R%3][C%3]` if `input[R//3][C//3]` is nonzero, else 0.

This is equivalent to: `output[R][C] = input[R//n][C//n] and input[R%n][C%n]` (using Python's `and` which returns the second operand when the first is truthy, or 0 when falsy).

**Verification with Example 1:** Input[0][0]=0 → block(0,0) is zeros ✓; Input[0][1]=7 → block(0,1) is the input pattern ✓. All blocks match.

**Verification with Example 4:** Input[1][1]=0 → center block is zeros ✓; Input[0][0]=6 → block(0,0) is input pattern ✓.

```python
def p(g):n=len(g);return[[g[i//n][j//n]and g[i%n][j%n]for j in range(n*n)]for i in range(n*n)]
```