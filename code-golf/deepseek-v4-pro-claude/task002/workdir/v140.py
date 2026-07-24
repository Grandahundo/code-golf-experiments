def p(g):
 g=[[x or 4for x in r]for r in g];H=len(g)
 def f(r,c):
  R=g[r]
  while H>r>=0<=c<H>3<R[c]:R[c]=0;f(r,c+1);f(r,c-1);f(r-1,c);r+=1;R=g[r*(r<H)]
 f(0,0);f(~-H,~-H)
 return g
