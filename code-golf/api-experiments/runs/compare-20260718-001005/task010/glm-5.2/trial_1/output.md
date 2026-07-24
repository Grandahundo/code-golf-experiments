```python
def p(g):
 h=len(g);w=len(g[0])
 C={c:sum(g[r][c]>4 for r in range(h))for c in range(w)}
 m={c:i+1 for i,c in enumerate(sorted(C,key=C.get,reverse=1))}
 return[[m[c]*(g[r][c]>4)or g[r][c]for c in range(w)]for r in range(h)]
```