def p(g):
 H=len(g)
 def f(r,c):
  if H>r>=0<=c<H>0==g[r][c]:g[r][c]=5;[(f(r+a,c),f(r,c+a))for a in(1,-1)]
 [f(i,j)or f(j,i)for i in range(H)for j in(0,H-1)]
 return[[x%5or 4 for x in r]for r in g]
