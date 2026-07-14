def p(g):
 o=[r[:]for r in g];L=len(g);w=len(g[0])
 for r in range(L):
  for c in range(w-1,-1,-1):
   if(v:=g[r][c])and(r<L-1 and v in g[r+1])and(g[r+1][c]!=v or g[r][c+1:c+2]==[v]):o[r][c]=0;o[r][c+1]=v
 return o
