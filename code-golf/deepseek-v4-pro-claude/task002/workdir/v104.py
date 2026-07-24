def p(g):
 H=len(g);g=[[x or 4for x in r]for r in g]
 def f(r,c):
  while H>r>=0<=c<H>3<g[r][c]:g[r][c]=0;f(r+1,c);f(r-1,c);f(r,c-1);c+=1
 for i in range(H):f(i,0)
 return g
