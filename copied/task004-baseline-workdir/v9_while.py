def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in range(h)];R=0;r=h
 while r:
  r-=1;N=0;c=w
  while c:
   c-=1;v=g[r][c]
   if v:N|=1<<v;o[r][c+(R>>v&1and(g[r+1][c]!=v or c+1<w and g[r][c+1]==v))]=v
  R=N
 return o
