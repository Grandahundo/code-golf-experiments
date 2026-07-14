def p(g):
 m=[0]*10
 for r in g[::-1]:
  for j,v in[*enumerate(r)][::-1]:
   if v:t=m[v];m[v]=t or j;t and j<t and(r[j+1]=v,r[j]=0)
 return g