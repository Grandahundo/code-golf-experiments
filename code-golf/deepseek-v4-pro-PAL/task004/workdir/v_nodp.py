def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 for r in range(h):
  for c in range(w):
   if g[r][c]:
    s=(r+1==h or any(g[r+1])<1)and(c>0<g[r][c-1]or c+1<w>g[r][c+1])or r+1<h and g[r+1][c]and(r+2==h or any(g[r+2])<1)and(c>0<g[r+1][c-1]or c+1<w>g[r+1][c+1])
    o[r][c+(s<1)]=g[r][c]
 return o
