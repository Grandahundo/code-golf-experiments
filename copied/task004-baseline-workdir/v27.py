def p(g,m={}):
 for r in g[::-1]:
  for j,v in[*enumerate(r)][::-1]:
   if v:a=m[v]=m.get(v,(r,j));r[j+(r!=a[0]and j!=a[1])]=v;r[j]*=r==a[0]or j==a[1]
 return g