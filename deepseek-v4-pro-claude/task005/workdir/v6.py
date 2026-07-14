def p(g):
 C={}
 for r in range(21):
  for c in range(21):
   if g[r][c]:C[g[r][c]]=C.get(g[r][c],[])+[(r,c)]
 M=max((v for v,p in C.items()if max(r for r,c in p)-min(r for r,c in p)<3and max(c for r,c in p)-min(c for r,c in p)<3),key=lambda v:len(C[v]))
 P=[(r,c)for r,c in C[M]];R=min(r for r,c in P);C0=min(c for r,c in P)
 P=[(r-R,c-C0)for r,c in P];o=[[0]*21 for _ in[0]*21]
 for i,j in P:
  x,y=R+i,C0+j
  if-1<x<21and-1<y<21:o[x][y]=M
 for r in range(21):
  for c in range(21):
   v=g[r][c]
   if v and v!=M:
    ar=r-(r-R)%4;ac=c-(c-C0)%4
    dr=(ar-R)//4;dc=(ac-C0)//4
    a,b=ar,ac
    while-4<a<25and-4<b<25:
     for i,j in P:
      x,y=a+i,b+j
      if-1<x<21and-1<y<21:o[x][y]=v
     if dr==dc==0:break
     a+=dr*4;b+=dc*4
 return o
