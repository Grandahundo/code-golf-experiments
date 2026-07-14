def p(g):
 h,w=len(g),len(g[0]);g=g+[[0]*w];o=[[0]*w for _ in[0]*h];r=h
 while r:
  r-=1;x=g[r];y=g[r+1]
  for c in range(w):
   if x[c]:o[r][c+(x[c]in y and(y[c]<1 or c+1<w and x[c+1]>0))]=x[c]
 return o
