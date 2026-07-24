```python
def p(g):
 L=[(len(g),0)]*len(g[0])
 for k,(r,c)in enumerate(sorted((c.index(5),i)for i,c in enumerate(zip(*g))if5in c),1):L[c]=(r,k)
 return[[r>=t andk or0for t,k in L]for r in range(len(g))]
```