def p(g):
 H=len(g);G=lambda r,c:0<=r<H>c>=0 and g[r][c]
 for _ in g*4:
  for r in range(H):
   for c in range(H):
    if g[r][c]<1 and(r*c*(H+~r)*(H+~c)==0 or -2 in(G(r+1,c),G(r-1,c),G(r,c+1),G(r,c-1))):g[r][c]=-2
 return[[(x or 4)*(x>-2)for x in r]for r in g]
