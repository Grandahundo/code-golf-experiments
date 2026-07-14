def p(g):
 H=len(g);g=[[x or 4 for x in r]for r in g]
 def f(r,c):
  if H>r>=0<=c<H<4+g[r][c]:g[r][c]=0;[f(r+a,c+b)for a,b in zip((1,3,0,0),(0,0,1,3))]
 for i in range(H):f(i,0);f(0,i)
 return g
