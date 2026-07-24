def p(g):
 H=len(g);g=[[x or 4 for x in r]for r in g]
 for k in g*H:
  for r in range(H):
   for c in range(H):
    if g[r][c]>3and(r*c*(r-H+1)*(c-H+1)<1 or 0in(g[r-1][c],g[r+1][c],g[r][c-1],g[r][c+1])):g[r][c]=0
 return g
