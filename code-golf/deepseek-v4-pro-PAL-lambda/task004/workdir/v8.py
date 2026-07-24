def p(g):
 h,w=len(g),len(g[0])
 g=g+[[0]*w]
 o=[[0]*w for _ in range(h)]
 r=h
 while r:
  r-=1
  for c in range(w):
   v=g[r][c]
   if v:
    t=v in g[r+1]and(g[r+1][c]<1 or c+1<w and g[r][c+1]>0)
    o[r][c+t]=v
 return o
