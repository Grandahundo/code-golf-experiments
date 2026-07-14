def p(g):
 H=len(g);g=[[x or 4for x in r]for r in g]
 def f(r,c):
  while H>r>=0<=c<H>3<g[r][c]:
   d=c
   while H>d>=0and g[r][d]>3:g[r][d]=0;f(r-1,d);f(r+1,d);d+=1
   d=c-1
   while d>=0and g[r][d]>3:g[r][d]=0;f(r-1,d);f(r+1,d);d-=1
   break
 for i in range(H):f(i,0);f(i,~-H)
 return g
