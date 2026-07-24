```python
def p(g):
 d={}
 for r in range(0,len(g)-1,3):
  for c in range(0,len(g[0])-1,3):
   v=g[r][c]
   if v:d[v]=d.get(v,[])+[(r//3,c//3)]
 for v,p in d.items():
  for i,j in p:
   J=[jj for ii,jj in p if ii==i]
   for jj in range(min(J),max(J)+1):
    for r in(3*i,3*i+1):g[r][3*jj:3*jj+2]=[v]*2
   I=[ii for ii,jj in p if jj==j]
   for ii in range(min(I),max(I)+1):
    for r in(3*ii,3*ii+1):g[r][3*j:3*j+2]=[v]*2
 return g
```