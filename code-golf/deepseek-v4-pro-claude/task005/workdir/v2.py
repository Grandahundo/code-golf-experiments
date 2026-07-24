def p(g):
 S=len(g)
 m=max((sum(g[r+i][c+j]>0for i in(0,1,2)for j in(0,1,2)),r,c)for r in range(S-2)for c in range(S-2));R,C=m[1],m[2]
 P=[(i,j)for i in(0,1,2)for j in(0,1,2)if g[R+i][C+j]];M=g[R+P[0][0]][C+P[0][1]]
 o=[[0]*S for _ in[0]*S]
 for r in(0,4,-4):
  for c in(0,4,-4):
   v=M if r==c==0 else 0
   if not v:
    for i in(0,1,2):
     for j in(0,1,2):
      if-1<R+r+i<S and-1<C+c+j<S and g[R+r+i][C+c+j]:v=g[R+r+i][C+c+j];break
     if v:break
   if v:
    a,b=R,C
    while-4<a<S+4and-4<b<S+4:
     for i,j in P:
      x,y=a+i,b+j
      if-1<x<S and-1<y<S:o[x][y]=v
     if r==c==0:break
     a+=r;b+=c
 return o
