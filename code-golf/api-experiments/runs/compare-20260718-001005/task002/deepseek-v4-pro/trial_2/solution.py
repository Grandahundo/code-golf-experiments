def p(g):
 R,C=len(g),len(g[0])
 q=[(i,j)for i in range(R)for j in range(C)if(i*(i-R+1)*j*(j-C+1)==0)&(g[i][j]<1)]
 for i,j in q:g[i][j]=2
 while q:
  r,c=q.pop()
  for n,m in(r+1,c),(r-1,c),(r,c+1),(r,c-1):
   if(0<=n<R)&(0<=m<C)&(g[n][m]<1):g[n][m]=2;q+=(n,m),
 return[[[4,0,0,3][v]for v in r]for r in g]
