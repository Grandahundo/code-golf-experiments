def p(g):
 H=len(g);g=[[x or 4for x in r]for r in g]
 for k in g*H:
  for r in range(H):
   for c in range(H):
    if g[r][c]>3and(c%~-H<1or 0in(g[r-1][c],g[r][c-1],g[r][c+1-H*(c>H-2)],g[(r+1)%H][c])):g[r][c]=0
 return g
