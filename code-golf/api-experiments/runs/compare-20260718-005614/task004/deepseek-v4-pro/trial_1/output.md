```python
def p(g):
 a=[0]*10;b=[0]*10
 for r,w in enumerate(g):
  for c,v in enumerate(w):
   if v:a[v]=max(a[v],r);b[v]=max(b[v],c)
 o=[[0]*len(g[0])for _ in g]
 for r,w in enumerate(g):
  for c,v in enumerate(w):
   if v:o[r][c+(r<a[v] and c<b[v])]=v
 return o
```