def p(g):
 H=len(g)
 def f(r,c):
  if H>r>=0<=c<H>0==g[r][c]:g[r][c]=5;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
 for i in range(H*H):f(i//H*(i%H%~-H<1),i%H)
 return[[4*(x<1)or x%5for x in r]for r in g]
