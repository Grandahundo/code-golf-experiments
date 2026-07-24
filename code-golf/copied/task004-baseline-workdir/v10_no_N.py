def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in range(h)];S=0;r=h
 while r:
  r-=1;c=w
  while c:
   c-=1;v=g[r][c]
   if v:o[r][c+(S>>v&1and(g[r+1][c]!=v or c+1<w and g[r][c+1]==v))]=v;S|=1<<v
 return o
