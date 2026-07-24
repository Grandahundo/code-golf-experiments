```python
def p(g):
 w=len(g[0]);o=[[0]*w for _ in g];u={(i,j):v for i,r in enumerate(g)for j,v in enumerate(r)if v}
 while u:
  (i,j),v=u.popitem();c=[(i,j)];k=0
  while k<len(c):
   r,x=c[k];k+=1
   for dy in -1,0,1:
    for dx in -1,0,1:
     if dy|dx:
      nr=r+dy;nx=x+dx
      if u.get((nr,nx))==v:del u[(nr,nx)];c.append((nr,nx))
  R,C=max(c)
  for r,x in c:o[r][x if r==R or x==C else x+1]=v
 return o
```