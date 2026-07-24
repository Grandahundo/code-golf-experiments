def p(g):
 h,w=len(g),len(g[0])
 o=[[0]*w for _ in range(h)]
 s=set()
 r=h
 while r:
  r-=1
  for c in range(w):
   v=g[r][c]
   if v:
    t=v in s and(g[r+1][c]<1 or c+1<w and g[r][c+1]>0)
    o[r][c+t]=v
  s.update(g[r])
 return o
