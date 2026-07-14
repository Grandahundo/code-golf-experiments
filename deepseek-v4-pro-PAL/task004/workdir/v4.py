def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 B=lambda r,c:r<h and g[r][c]and(r+1==h or any(g[r+1])<1)and(c>0<g[r][c-1]or c+1<w>g[r][c+1])
 for r in range(h):
  for c in range(w):
   if g[r][c]:o[r][c+1-(B(r,c)or B(r+1,c))]=g[r][c]
 return o
