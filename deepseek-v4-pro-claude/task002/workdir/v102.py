def p(g):
 H=len(g);g=[[x or 4for x in r]for r in g]
 def f(r,c,d=1):
  while H>r>=0<=c<H>3<g[r][c]:g[r][c]=0;f(r,c+1);f(r,c-1);f(r+d,c,-d);r-=d
 for i in range(H):f(i,0);f(i,~-H)
 return g
