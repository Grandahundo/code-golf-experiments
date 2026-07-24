def p(g):
 R,C=max(((r,c)for r in range(19)for c in range(19)),key=lambda x:sum(g[x[0]+i][x[1]+j]>0for i in(0,1,2)for j in(0,1,2)))
 P=[(i,j)for i in(0,1,2)for j in(0,1,2)if g[R+i][C+j]];M=g[R+P[0][0]][C+P[0][1]];o=[[0]*21for _ in[0]*21]
 for r in(0,4,-4):
  for c in(0,4,-4):
   if r|c:a,b=R+r,C+c;v=[g[a+i][b+j]for i in(0,1,2)for j in(0,1,2)if g[a+i][b+j]]
   else:a,b,v=R,C,M
   if v:
    if r|c:v=v[0]
    while-4<a<25and-4<b<25:
     for i,j in P:
      x,y=a+i,b+j
      if-1<x<21and-1<y<21:o[x][y]=v
     if not r|c:break
     a+=r;b+=c
 return o
