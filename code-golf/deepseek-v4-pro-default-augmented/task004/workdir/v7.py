def p(g):
 h=len(g);w=len(g[0]);o=[[0]+r[:-1]for r in g]
 for r in range(h):
  for c in range(w):
   if v:=g[r][c]:
    a=r and v in g[r-1];b=r<h-1 and v in g[r+1]
    if not(a<1 or b and g[r+1][c]!=v):o[r][c]=v;o[r][c+1]=0
 return o
