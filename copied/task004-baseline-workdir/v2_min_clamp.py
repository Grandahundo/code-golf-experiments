def p(g):
 h=len(g);w=len(g[0])
 R=[0]*h
 M={}
 for r in range(h):
  for c in range(w):
   v=g[r][c]
   if v:R[r]|=1<<v;M[v]=max(M.get(v,0),c)
 o=[[0]*w for _ in range(h)]
 for r in range(h):
  for c in range(w):
   v=g[r][c]
   if v:
    if r+1<h and R[r+1]>>v&1:
     o[r][min(c+1,M[v])]=v
    else:o[r][c]=v
 return o
