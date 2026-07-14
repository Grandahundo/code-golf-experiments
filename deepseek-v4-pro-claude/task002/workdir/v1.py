def p(g):
 g=[r[:]for r in g];H=len(g);W=len(g[0])
 s=[(r,c)for r in range(H)for c in range(W)if g[r][c]<1and(r in(0,H-1)or c in(0,W-1))]
 for r,c in s:
  g[r][c]=-1
  for dr,dc in((1,0),(-1,0),(0,1),(0,-1)):
   if 0<=r+dr<H and 0<=c+dc<W and g[r+dr][c+dc]<1:s+=[(r+dr,c+dc)]
 return[[4if x==0 else max(x,0)for x in r]for r in g]
