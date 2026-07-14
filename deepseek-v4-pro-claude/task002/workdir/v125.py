def p(g):
 g=[[x or 4for x in r]for r in g];H=len(g)
 def f(r,c):
  while H>r>=0<=c<H>3<g[r][c]:g[r][c]=0;f(r-1,c);[f(r,c+d)for d in(1,-1)];r+=1
 f(0,0);f(~-H,~-H)
 return g
