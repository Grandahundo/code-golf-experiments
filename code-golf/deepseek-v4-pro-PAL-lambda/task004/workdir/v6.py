def p(g):
 h=len(g);w=len(g[0])
 g=[r+[0]for r in g]+[[0]*(w+1)]
 o=[[0]*w for _ in range(h)]
 s=set()
 for r in range(h-1,-1,-1):
  for c in range(w):
   v=g[r][c]
   if v:
    if v in s and not(g[r+1][c]and g[r][c+1]<1):o[r][c+1]=v
    else:o[r][c]=v
  s|={c for c in g[r]if c}
 return o
