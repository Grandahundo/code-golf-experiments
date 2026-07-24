Looking at the examples, I need to find the pattern:

1. All 1s become 2s in the output
2. The output extends the input by half its length (6→9 rows)
3. The extension follows the periodic pattern of the input rows

Let me verify the period-finding approach:
- **Ex 1**: rows have period 4 (g[4:]==g[:-4]). Extended rows 7,8,9 = rows 3,4,1 ✓
- **Ex 2**: rows have period 2 (g[2:]==g[:-2]). Extended rows 7,8,9 = rows 1,2,1 ✓  
- **Ex 3**: rows have period 3 (g[3:]==g[:-3]). Extended rows 7,8,9 = rows 1,2,3 ✓

The rule: find smallest period P where `g[P:]==g[:-P]`, then extend to `len(g)*3//2` rows using `g[i%P]`, mapping 1→2.

```python
def p(g):
 P=1
 while g[P:]!=g[:-P]:P+=1
 return[[x*2for x in g[i%P]]for i in range(len(g)*3//2)]
```