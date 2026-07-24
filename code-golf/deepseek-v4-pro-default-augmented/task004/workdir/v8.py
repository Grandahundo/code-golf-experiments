def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g];s=set()
 for r in range(h-1,-1,-1):
  for c in range(w):
   if v:=g[r][c]:
    if v in s:
     if g[r+1][c]==v and g[r][c+1:c+2]!=[v]:o[r][c]=v
     else:o[r][c+1]=v
    else:s.add(v);o[r][c]=v
 return o
