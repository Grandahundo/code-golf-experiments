def p(g):
 H=len(g)
 for _ in sum(g,[]):
  for r in range(H):
   for c in range(H):
    if g[r][c]==0and(r%~-H*(c%~-H)<1or-1in(g[r-1][c],g[r+1][c],g[r][c-1],g[r][c+1])):g[r][c]=-1
 return[[(x or 4)*(x>-1)for x in r]for r in g]
