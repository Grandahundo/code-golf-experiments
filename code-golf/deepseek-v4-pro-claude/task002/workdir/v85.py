def p(g):
 H=len(g);g=[[x or 4for x in r]for r in g]
 def f(r,c):
  if H>r>=0<=c<H>3<g[r][c]:g[r][c]=0;[f(r+a,c)or f(r,c+a)for a in(1,-1)]
 for i in range(H):f(i,0);f(0,i);f(i,H-1);f(H-1,i)
 return g
