def p(g,m={}):
 for r in g[::-1]:
  for j,v in[*enumerate(r)][::-1]:
   if v:m[v]=m.get(v)or(r,j);s=r!=m[v][0]and j!=m[v][1];r[j+s]=v;r[j]*=1-s
 return g
