def p(g):
 m={}
 for r in g[::-1]:
  for j in range(len(r))[::-1]:
   if v:=r[j]:m[v]=m.get(v,(r,j))
   if v and r-m[v][0]and j-m[v][1]:r[j]=0;r[j+1]=v
 return g