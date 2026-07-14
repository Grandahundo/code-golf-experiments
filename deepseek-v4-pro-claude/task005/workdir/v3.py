def p(g,S=21):
 m=max((sum(g[r+i][c+j]>0for i in(0,1,2)for j in(0,1,2)),r,c)for r in range(19)for c in range(19));R,C=m[1],m[2]
 P=[(i,j)for i in(0,1,2)for j in(0,1,2)if g[R+i][C+j]];M=g[R+P[0][0]][C+P[0][1]]
 o=[[0]*S for _ in[0]*S]
 for r in(0,4,-4):
  for c in(0,4,-4):
   if r|c:v=0;a,b=R+r,C+c
   else:v=M;a,b=R,C
   if not v:
    for i in(0,1,2):
     for j in(0,1,2):
      if-1<a+i<S and-1<b+j<S and g[a+i][b+j]:v=g[a+i][b+j];break
     if v:break
   if v:
    while-4<a<S+4and-4<b<S+4:
     for i,j in P:
      x,y=a+i,b+j
      if-1<x<S and-1<y<S:o[x][y]=v
     if not r|c:break
     a+=r;b+=c
 return o
