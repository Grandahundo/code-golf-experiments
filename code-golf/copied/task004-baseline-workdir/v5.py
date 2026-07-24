def p(g):
 a=[0]*10;b=[0]*10
 for r in g[::-1]:
  for j in range(len(r))[::-1]:
   if v:=r[j]:a[v]=a[v]or r;b[v]=b[v]or j;s=r!=a[v]and j!=b[v];r[j+s]=v;r[j]*=1-s
 return g