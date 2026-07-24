def p(g):
 H=len(g);g=[[x or 4for x in r]for r in g]
 def f(r,c):
  if H>r>=0<=c<H>3<g[r][c]:g[r][c]=0;[f(r+a,c+b)for a,b in zip((1,-1,0,0),(0,0,1,-1))]
 for i in range(H):f(i,0);f(i,H-1)
 return g
