def p(g):
 H=len(g);g=[[x or 4 for x in r]for r in g]
 for k in g*H:
  for r,R in enumerate(g):
   for c,x in enumerate(R):
    if x>3and(min(r,c,H+~r,H+~c)<1 or 0in(g[r-1][c],g[r-~0*(r<H-1)][c],R[c-1],R[c+1-H*(c>H-2)])):R[c]=0
 return g
