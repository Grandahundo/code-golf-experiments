def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 for r in range(h)[::-1]:
  for c in range(w):
   if g[r][c]:
    s=(r+1<h)*o[r+1][c]or(r+1==h or any(g[r+1])<1)and(c>0<g[r][c-1]or c+1<w>g[r][c+1])
    o[r][c+(s==0)]=g[r][c]
 return o
