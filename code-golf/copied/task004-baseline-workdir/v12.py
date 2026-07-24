def p(g):
 m={}
 for r in g[::-1]:
  for j,v in[*enumerate(r)][::-1]:
   if v:m[v]=m.get(v,(r,j))
   if v and r!=m[v][0]and j!=m[v][1]:r[j+1]=v;r[j]=0
 return g