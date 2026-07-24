def p(g):
 R=len(g);C=len(g[0])
 v=[C*[0]for _ in g]
 c=[]
 for i in range(R):
  for j in range(C):
   if g[i][j]and not v[i][j]:
    t=g[i][j];Q=[(i,j)];v[i][j]=1;s=[]
    while Q:
     x,y=Q.pop();s+=[(x,y)]
     for a,b in(x-1,y),(x+1,y),(x,y-1),(x,y+1):
      if 0<=a<R and 0<=b<C and not v[a][b] and g[a][b]==t:v[a][b]=1;Q+=[(a,b)]
    c+=[(t,s)]
 Z=max(c,key=lambda x:len(x[1]));A=Z[1]
 X=(min(x for x,y in A)+max(x for x,y in A))>>1
 Y=(min(y for x,y in A)+max(y for x,y in A))>>1
 P={(x-X,y-Y)for x,y in A}
 o=[C*[0]for _ in g]
 for x,y in A:o[x][y]=Z[0]
 for t,s in c:
  if s is A:continue
  f=0
  for u,v in s:
   if f:break
   for d,e in P:
    cx=u-d;cy=v-e
    if(cx-X)%4+(cy-Y)%4==0:
     if all((x-cx,y-cy)in P for x,y in s):f=1;U=cx-X;V=cy-Y;break
  if not f:continue
  x,y=cx,cy
  while 1:
   ok=0
   for d,e in P:
    nx,ny=x+d,y+e
    if 0<=nx<R and 0<=ny<C:o[nx][ny]=t;ok=1
   if not ok:break
   x+=U;y+=V
 return o
