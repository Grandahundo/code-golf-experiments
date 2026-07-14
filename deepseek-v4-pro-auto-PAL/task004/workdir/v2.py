def p(g):
 W=len(g[0]);b=[any(r)for r in g]+[0,0];o=[[0]*W for _ in g]
 for r,R in enumerate(g):
  m=max((i for i,x in enumerate(R)if x),default=0)
  for c,x in enumerate(R):
   if x:o[r][c+(b[r+1]and(b[r+2]or c<m))]=x
 return o
