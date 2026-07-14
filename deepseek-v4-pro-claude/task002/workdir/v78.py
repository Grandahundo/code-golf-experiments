def p(g):
 H=len(g);g=[[x or 4for x in r]for r in g]
 def f(r,c):
  if H>r>=0<=c<H>3<g[r][c]:
   g[r][c]=0
   for d in(1,-1):f(r+d,c);f(r,c+d)
 [f(i,j)or f(j,i)for i in range(H)for j in(0,H-1)]
 return g
