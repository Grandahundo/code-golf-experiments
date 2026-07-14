def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 for i in range(h*w):
  r=i//w;c=i%w
  if v:=g[r][c]:a=r and v in g[r-1];b=r<h-1 and v in g[r+1];o[r][c+(a<1 or b and g[r+1][c]!=v)]=v
 return o
