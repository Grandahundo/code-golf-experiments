def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 for r in range(h):
  for c in range(w):
   if v:=g[r][c]:
    b=r<h-1 and v in g[r+1]
    o[r][c+(b and(g[r+1][c]!=v or g[r][c+1:c+2]==[v]))]=v
 return o
