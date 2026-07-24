def p(g):
 R=len(g);C=len(g[0]);n=(R+1)//3;m=(C+1)//3
 c=[[g[3*i][3*j]for j in range(m)]for i in range(n)]
 o=[r[:]for r in c]
 def F(a,b):
  for i in range(len(a)):
   for k in range(1,10):
    x=[j for j,v in enumerate(a[i])if v==k]
    if x[1:]:
     for j in range(x[0],x[-1]+1):b[i][j]=b[i][j]or k
 F(c,o)
 t=list(zip(*c));u=[list(x)for x in zip(*o)];F(t,u)
 o=list(zip(*u))
 r=[row[:]for row in g]
 for i in range(n):
  a=3*i
  for j in range(m):
   b=3*j;r[a][b]=r[a][b+1]=r[a+1][b]=r[a+1][b+1]=o[i][j]
 return r
