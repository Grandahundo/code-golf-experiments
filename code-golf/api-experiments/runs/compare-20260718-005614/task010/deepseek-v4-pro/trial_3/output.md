```python
def p(G):
 m={};n=1
 for r in G:
  for j,v in enumerate(r):
   if v:
    if j not in m:m[j]=n;n+=1
    r[j]=m[j]
 return G
```