def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 for c in range(w):
  s=0
  for r in range(h)[::-1]:
   v=g[r][c]
   if v:s|=v and(c>0<g[r][c-1]or c+1<w>g[r][c+1])and(r+1==h or any(g[r+1])<1);o[r][c+1-s]=v
   else:s=0
 return o