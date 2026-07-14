def p(g):
 w=len(g[0]);g=g+[[0]*w];o=[[0]*w for _ in g[:-1]]
 for r,R in enumerate(g[:-1]):
  for c,v in enumerate(R):
   if v and v in g[r+1]and(g[r+1][c]!=v or g[r][c+1:c+2]==[v]):o[r][c+1]=v
   elif v:o[r][c]=v
 return o
