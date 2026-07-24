```python
def p(g):k=len({*sum(g,[])}-{0})or 1;d={(i+j)%k:v for i,r in enumerate(g)for j,v in enumerate(r)if v};return[[d.get((i+j)%k,0)for j in range(len(g[0]))]for i in range(len(g))]
```