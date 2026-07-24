def p(g):
 H=len(g)
 for k in g*H:
  for r in range(H):
   for c in range(H):
    if g[r][c]==0and(r*c*(r-H+1)*(c-H+1)==0or-1in(g[r-1][c],g[r+1][c],g[r][c-1],g[r][c+1])):g[r][c]=-1
 return[[(x or 4)*(x>-1)for x in r]for r in g]
