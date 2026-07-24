def p(g):
 m={}
 for r in g[::-1]:
  for j in range(len(r))[::-1]:
   if v:=r[j]:m[v]=m.get(v,(r,j));r[j+(s:=(r!=m[v][0])*(j!=m[v][1]))]=v;r[j]*=s^1
 return g