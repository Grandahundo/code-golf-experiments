def p(g):
 g=[[x or 4for x in r]for r in g];H=len(g)
 def f(r,c):
  while H>r>=0<=c<H>3<g[r][c]:g[r][c]=0;f(r,c+1);f(r,c-1);f(r-1,c);r+=1
 [*map(f,(0,~-H),(0,~-H))]
 return g
