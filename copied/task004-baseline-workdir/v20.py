def p(g):
 m=0
 for i in range(len(g))[::-1]:
  r=g[i];s=m
  for j in range(len(r)-1)[::-1]:
   if v:=r[j]:
    m|=1<<v
    if r[j+1]==0and s>>v&1and g[i+1][j]-v:r[j+1]=v;r[j]=0
 return g
