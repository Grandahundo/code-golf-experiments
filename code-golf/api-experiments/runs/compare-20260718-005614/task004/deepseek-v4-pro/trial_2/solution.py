def p(g):
 o=[[0]*len(g[0]) for _ in g]
 d=[[]for _ in range(10)]
 for i,r in enumerate(g):
  for j,x in enumerate(r):
   if x:d[x].append((i,j))
 for v in range(1,10):
  c=d[v]
  if c:
   m=0;k={}
   for r,x in c:m=max(m,r);k[r]=max(k.get(r,0),x)
   for r,x in c:o[r][x+(r<m-1 or r==m-1 and x<k[r])]=v
 return o
