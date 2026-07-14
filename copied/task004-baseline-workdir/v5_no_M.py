def p(g):
 h=len(g);w=len(g[0])
 o=[[0]*w for _ in range(h)]
 R=0
 for r in range(h)[::-1]:
  N=0
  for c in range(w)[::-1]:
   v=g[r][c]
   if v:
    N|=1<<v
    o[r][c+(R>>v&1and not(g[r+1][c]==v!=(c+1<w and g[r][c+1])))]=v
  R=N
 return o
