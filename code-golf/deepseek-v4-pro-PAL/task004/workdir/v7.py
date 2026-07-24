def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 for c in range(w):
  s=0
  for r in range(h)[::-1]:
   if g[r][c]:
    if s or(c>0<g[r][c-1]or c+1<w>g[r][c+1])and(r+1==h or any(g[r+1])<1):s=1
    else:s=0
    o[r][c+1-s]=g[r][c]
   else:s=0
 return o
