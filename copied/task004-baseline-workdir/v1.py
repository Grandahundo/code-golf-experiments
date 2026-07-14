def p(g):
 w=len(g[0]);o=[[0]*w for _ in g];m={}
 for r in range(len(g))[::-1]:
  for c in range(w)[::-1]:
   if v:=g[r][c]:m[v]=m.get(v,(r,c));o[r][c+(r!=m[v][0]and c!=m[v][1])]=v
 return o