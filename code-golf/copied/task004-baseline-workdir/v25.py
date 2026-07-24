def p(g,m={}):
 for r in g[::-1]:
  for j,v in[*enumerate(r)][::-1]:
   if v:a=m[v]=m.get(v,(r,j));s=r!=a[0]and j!=a[1];r[j+s]=v;r[j]*=1-s
 return g