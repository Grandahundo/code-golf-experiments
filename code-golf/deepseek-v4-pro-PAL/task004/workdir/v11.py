def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g];e=[any(r)for r in g]+[0,0]
 for r in range(h)[::-1]:
  for c in range(w):
   if g[r][c]:
    s=not e[r+1]and(c>0<g[r][c-1]or c+1<w>g[r][c+1])or r+1<h and g[r+1][c]and not e[r+2]and(c>0<g[r+1][c-1]or c+1<w>g[r+1][c+1])
    o[r][c+(s<1)]=g[r][c]
 return o
