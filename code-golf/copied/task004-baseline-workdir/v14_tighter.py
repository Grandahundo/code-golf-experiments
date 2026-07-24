def p(g):
 w=len(g[0]);o=[[0]*w for _ in g];R={};C={};r=len(g)
 while r:
  r-=1;c=w
  while c:
   c-=1;v=g[r][c]
   if v:R[v]=R.get(v,r);C[v]=C.get(v)or c;o[r][c+(r!=R[v]and c<C[v])]=v
 return o
