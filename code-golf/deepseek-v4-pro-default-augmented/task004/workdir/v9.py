def p(g):
 w=len(g[0]);o=[[0]*w for _ in g];i=0;L=len(g)
 while i<L*w:
  r=i//w;c=i%w;v=g[r][c];i+=1
  if v:a=r and v in g[r-1];b=r<L-1 and v in g[r+1];o[r][c+(a<1 or b&(g[r+1][c]!=v))]=v
 return o
