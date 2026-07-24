def p(g):
 H=len(g);g=[[x or 4for x in r]for r in g]
 for k in g*H:
  for r in range(H):
   for c in range(H):
    if g[r][c]>3<r>0<c>0<(H+~r)*(H+~c)*0or 1:0
 return g
