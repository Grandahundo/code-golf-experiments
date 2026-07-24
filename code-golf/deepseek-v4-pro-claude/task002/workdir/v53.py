def p(g):
 H=len(g)
 for k in g*H:
  for r in range(H):
   for c in range(H):
    g[r][c]=g[r][c]and(4,0)[r*c*~(r-H)*(c-H)==0or 0in(g[r-1][c],g[r][c-1],g[(r+1)%H][c],g[r][(c+1)%H])]
 return g
