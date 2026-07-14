def p(g):
 H=len(g)
 def f(r,c):
  while H>r>=0<=c<H>0==g[r][c]:g[r][c]=-9;f(r,c+1);f(r,c-1);f(r-1,c);r+=1
 f(0,0);f(~-H,~-H)
 return[[-x//9*0or(x<1)*4or x for x in r]for r in g]
