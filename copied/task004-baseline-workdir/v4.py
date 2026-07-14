def p(g):
 a=[0]*10;b=[0]*10
 for i in range(len(g))[::-1]:
  r=g[i]
  for j in range(len(r))[::-1]:
   if v:=r[j]:
    a[v]=a[v]or i;b[v]=b[v]or j
    if i-a[v]and j-b[v]:r[j]=0;r[j+1]=v
 return g