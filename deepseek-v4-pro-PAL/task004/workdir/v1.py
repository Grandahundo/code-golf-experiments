def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in range(h)]
 b=set()
 for r in range(h):
  for c in range(w):
   if g[r][c]and(r+1==h or g[r+1][c]==0):
    if(c>0and g[r][c-1])or(c+1<w and g[r][c+1]):
     if not((r+1<h and c>0and g[r+1][c-1])or(r+1<h and c+1<w and g[r+1][c+1])):
      b.add((r,c))
 for r in range(h):
  for c in range(w):
   if g[r][c]:
    if(r,c)in b or(r+1<h and(r+1,c)in b):o[r][c]=g[r][c]
    elif c+1<w:o[r][c+1]=g[r][c]
 return o
