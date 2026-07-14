def p(g):
 H=len(g);g=[[x or 4*(0<i<~-H<j+2>2)for j,x in enumerate(r)]for i,r in enumerate(g)]
 for k in g*H:
  for r in range(H):
   for c in range(H):
    if g[r][c]>3and 0in(g[r-1][c],g[r+1-H][c],g[r][c-1],g[r][c+1-H]):g[r][c]=0
 return g
