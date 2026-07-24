def p(g):
 H=len(g)
 def f(r,c):
  if H>r>=0<=c<H>0==g[r][c]:g[r][c]=-1;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
 for i in range(H):f(i,0);f(i,H-1);f(0,i);f(H-1,i)
 return[[(x or 4)*(x>-1)for x in r]for r in g]
