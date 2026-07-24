def p(g):
 n=len(g);m=len(g[0]);L=g[2][0];R=-~n//3;C=-~m//3
 b=[[(v:=g[i*3][j*3])*(v==g[i*3][j*3+1]==g[i*3+1][j*3]==g[i*3+1][j*3+1])for j in range(C)]for i in range(R)]
 for i in range(R):
  d={}
  for j in range(C):
   v=b[i][j]
   if v:d[v]=d.get(v,[])+[j]
  for v,x in d.items():
   for j in range(min(x),max(x)+1):b[i][j]=v
 for j in range(C):
  d={}
  for i in range(R):
   v=b[i][j]
   if v:d[v]=d.get(v,[])+[i]
  for v,x in d.items():
   for i in range(min(x),max(x)+1):b[i][j]=v
 return[[L if i%3==2or j%3==2else b[i//3][j//3]for j in range(m)]for i in range(n)]
