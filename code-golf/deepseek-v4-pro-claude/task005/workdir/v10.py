def p(g):
 R,C=max(((r,c)for r in range(19)for c in range(19)),key=lambda x:sum(g[x[0]+i][x[1]+j]>0for i in(0,1,2)for j in(0,1,2)))
 P=[(i,j)for i in(0,1,2)for j in(0,1,2)if g[R+i][C+j]];o=[[0]*21 for _ in[0]*21]
 for r in range(21):
  for c in range(21):
   if v:=g[r][c]:
    a=r-(r-R)%4;b=c-(c-C)%4;d=(a-R)//4;e=(b-C)//4
    while-4<a<25and-4<b<25:
     for i,j in P:
      x,y=a+i,b+j
      if-1<x<21and-1<y<21:o[x][y]=v
     if d==e==0:break
     a+=d*4;b+=e*4
 return o
