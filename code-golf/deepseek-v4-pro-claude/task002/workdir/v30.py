def p(g):
 H=len(g)
 def f(r,c):
  if H>r>=0<=c<H>0==g[r][c]:g[r][c]=-1;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
 for i in range(H*4):f(i//4%H*(i%4//2)or 0,i//4%H)if 0 else 0
 return g
