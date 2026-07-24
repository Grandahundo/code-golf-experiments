def p(g):
 g=[[x or 4for x in r]for r in g];H=len(g)
 def f(r,c):
  try:
   while r>=0<=c<H>3<g[r][c]:g[r][c]=0;f(r,c+1);f(r,c-1);f(r-1,c);r+=1
  except:0
 f(0,0);f(~-H,~-H)
 return g
