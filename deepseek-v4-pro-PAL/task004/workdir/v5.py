def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 for r in range(h)[::-1]:
  for c in range(w):
   if g[r][c]:o[r][c+(r+1<h and o[r+1][c]==0)]=g[r][c]
 return o
