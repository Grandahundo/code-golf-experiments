def p(g):
 w=len(g[0]);o=[[0]*w for _ in g];R=[0]*10;C=[0]*10;r=len(g)
 while r:
  r-=1;c=w
  while c:
   c-=1;v=g[r][c]
   if v:
    if not R[v]:R[v]=r
    if not C[v]:C[v]=c
    o[r][c+(r!=R[v]and c<C[v])]=v
 return o
