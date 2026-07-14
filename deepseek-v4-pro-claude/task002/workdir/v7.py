def p(g):
 g=[r[:]for r in g];H=len(g);W=len(g[0]);R=range
 s=[(r,c)for r in R(H)for c in R(W)if g[r][c]<1and r%(H-1)*(c%(W-1))<1]
 for r,c in s:
  g[r][c]=-1
  for a,b in((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
   if H>a>=0<=b<W and g[a][b]==0:s+=(a,b),
 return[[(x or 4)*(x>-1)for x in r]for r in g]
