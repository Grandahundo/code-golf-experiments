def p(g):
 g=[[x or 4for x in r]for r in g];H=len(g)
 def f(r,c):
  while-1<r<H>c>-1and 3<g[r][c]:g[r][c]=0;f(r,c+1);f(r,c-1);f(r-1,c);r+=1
 f(0,0);f(~-H,~-H)
 return g
