def p(g):
 h=len(g);w=len(g[0])
 o=[[0]*w for _ in range(h)]
 s=set()
 for r in range(h-1,-1,-1):
  for c in range(w):
   v=g[r][c]
   if v:
    if v in s:
     if r+1<h and g[r+1][c]and(c+1>=w or g[r][c+1]==0):o[r][c]=v
     else:o[r][c+1]=v
    else:o[r][c]=v
  s|={c for c in g[r]if c}
 return o
