def p(g):
 H=len(g);g=[[x or 4 for x in r]for r in g]
 for i in range(H):g[i][0]=g[i][-1]=g[0][i]=g[-1][i]=0
 for k in g*H:
  for r in range(1,H-1):
   for c in range(1,H-1):
    if g[r][c]>3and 0in(g[r-1][c],g[r+1][c],g[r][c-1],g[r][c+1]):g[r][c]=0
 return g
