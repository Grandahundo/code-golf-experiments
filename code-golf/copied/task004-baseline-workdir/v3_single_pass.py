def p(g):
 h=len(g);w=len(g[0])
 o=[[0]*w for _ in range(h)]
 R=0;M={}
 for r in range(h-1,-1,-1):
  N=0
  for c in range(w-1,-1,-1):
   v=g[r][c]
   if v:
    N|=1<<v
    M[v]=max(M.get(v,0),c)
    if R>>v&1:o[r][min(c+1,M[v])]=v
    else:o[r][c]=v
  R=N
 return o
