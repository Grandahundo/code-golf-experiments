def p(g):
 h=len(g);w=len(g[0])
 o=[[0]*w for _ in range(h)]
 R=0;M={}
 for r in range(h)[::-1]:
  N=0
  for c in range(w)[::-1]:
   v=g[r][c]
   if v:
    N|=1<<v
    M[v]=max(M.get(v,0),c)
    o[r][R>>v&1and min(c+1,M[v])or c]=v
  R=N
 return o
