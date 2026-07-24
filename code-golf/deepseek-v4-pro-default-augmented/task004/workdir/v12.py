def p(g):
 o=[[0]*len(g[0])for _ in g];L=len(g);w=len(g[0])
 for i in range(L*w):
  r=i//w;c=i%w;v=g[r][c]
  if v:a=r and v in g[r-1];b=r<L-1 and v in g[r+1];o[r][c+(a<1or b&(g[r+1][c]!=v))]=v
 return o
