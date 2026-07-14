def p(g):
 o=[r[:]for r in g]
 for r in range(L:=len(g)):
  for c in range(len(g[0])):
   if(v:=g[r][c])and(r<L-1 and v in g[r+1])and(g[r+1][c]!=v or g[r][c+1:c+2]==[v]):o[r][c]=0;o[r][c+1]=v
 return o
