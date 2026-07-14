def p(g):
 w=len(g[0]);g=g+[[0]*w];o=[[0]*w for _ in g[:-1]];r=len(g)-1
 while r:
  r-=1;x=g[r];y=g[r+1]
  for c in range(w):o[r][c+(x[c]and x[c]in y and(y[c]<1 or c+1<w and x[c+1]>0))]=x[c]
 return o
