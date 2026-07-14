def p(g,r=0,c=-1):
 if{r,c}=={-1}:
  H=len(g);g=[[x or 4for x in r]for r in g]
  for i in range(H):p(g,i,0);p(g,i,~-H)
  return g
 H=len(g)
 if H>r>=0<=c<H>3<g[r][c]:g[r][c]=0;p(g,r,c+1);p(g,r,c-1);p(g,r-1,c)
