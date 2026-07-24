Looking at the examples, I need to find the pattern:

**Example 1:** Input rows have period 4 (r4=r0, r5=r1). Output extends to 9 rows using period 4: rows 6,7,8 = rows 2,3,0.

**Example 2:** Input has period 2. Output continues: rows 6,7,8 = rows 0,1,0.

**Example 3:** Input has period 3. Output continues: rows 6,7,8 = rows 0,1,2.

In all cases, 1→2 color change is applied. The rule: find minimal period P, then output = first `3n//2` rows of the periodic extension, with 1s replaced by 2s.

Verification for Example 1: P=4 (since g[:2]==g[4:]). Output rows: g[0],g[1],g[2],g[3],g[0],g[1],g[2],g[3],g[0] with 1→2 → matches ✓

```python
def p(g):
 n=len(g);P=next(P for P in range(1,n+1)if g[:n-P]==g[P:])
 return[[c*2for c in g[i%P]]for i in range(3*n//2)]
```