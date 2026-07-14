def p(g):
 w=len(g[0]);o=[[0]*w for _ in g];R={};C={}
 for r in range(len(g))[::-1]:
  for c in range(w)[::-1]:
   v=g[r][c]
   if v:R[v]=R.get(v,r);C[v]=max(C.get(v,0),c);o[r][[min(c+1,C[v]),c][r==R[v]]]=v
 return o
