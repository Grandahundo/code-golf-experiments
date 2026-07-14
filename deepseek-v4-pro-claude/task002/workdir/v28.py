def p(g):
 H=len(g);e=H-1
 def f(r,c):
  if H>r>=0<=c<H>0==g[r][c]:g[r][c]=-1;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
 [f(i,j)for i in range(H)for j in range(H)if i%e*(j%e)<1]
 return[[(x or 4)*(x>-1)for x in r]for r in g]
