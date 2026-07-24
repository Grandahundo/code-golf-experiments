def p(g):
 H=len(g);g=[[x or 4for x in r]for r in g];s=[(i,j)for i in range(H)for j in(0,~-H)]
 while s:
  r,c=s.pop()
  if H>r>=0<=c<H>3<g[r][c]:g[r][c]=0;s+=[(r+1,c),(r-1,c),(r,c+1),(r,c-1)]
 return g
