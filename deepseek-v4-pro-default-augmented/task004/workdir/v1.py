def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in[0]*h]
 for r in range(h):
  for c in range(w):
   if v:=g[r][c]:
    a=r and v in g[r-1];b=r<h-1 and v in g[r+1]
    o[r][c+(not a or b and g[r+1][c]!=v)]=v
 return o
