```python
def p(g):
    h=len(g);w=len(g[0])
    o=[[0]*w for _ in g]
    for r in range(h):
        m=max((c for c in range(w) if r<h-1 and g[r+1][c]),default=0)
        for c in range(w):
            if g[r][c]:o[r][c+(r<h-1 and c<m)]=g[r][c]
    return o
```