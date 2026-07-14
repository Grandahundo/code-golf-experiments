def p(g):
 h=len(g);w=len(g[0])
 R=[0]*h
 for r in range(h):
  for c in range(w):
   v=g[r][c]
   if v:R[r]|=1<<v
 o=[[0]*w for _ in range(h)]
 for r in range(h):
  for c in range(w):
   v=g[r][c]
   if v:
    if r+1<h and R[r+1]&1<<v:
     if r+1<h and c>0 and g[r+1][c-1]==v and(c<1 or g[r][c-1]-v)and(c+1>=w or g[r][c+1]-v):
      o[r][c]=v
     else:o[r][c+1]=v
    else:o[r][c]=v
 return o
