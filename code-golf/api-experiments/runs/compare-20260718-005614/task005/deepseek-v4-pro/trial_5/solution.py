def p(g):
 R=len(g);C=len(g[0])
 d={}
 for r in range(R):
  for c in range(C):
   v=g[r][c]
   if v:d[v]=d.get(v,[])+[(r,c)]
 m=max(d,key=lambda k:len(d[k]))
 P=d[m]
 tr,tc=[sum(x)/len(P)for x in zip(*P)]
 r0=min(r for r,_ in P);r1=max(r for r,_ in P)
 c0=min(c for _,c in P);c1=max(c for _,c in P)
 o=[[0]*C for _ in range(R)]
 for r,c in P:o[r][c]=m
 for k,L in d.items():
  if k==m:continue
  u={*L}
  while u:
   r,c=u.pop()
   cmp=[(r,c)]
   i=0
   while i<len(cmp):
    r,c=cmp[i];i+=1
    for dr in(-1,0,1):
     for dc in(-1,0,1):
      if dr|dc:
       nr,nc=r+dr,c+dc
       if(nr,nc)in u:u.remove((nr,nc));cmp.append((nr,nc))
   cr,cc=[sum(x)/len(cmp)for x in zip(*cmp)]
   dr=(cr>tr)-(cr<tr)
   dc=(cc>tc)-(cc<tc)
   if dr==0==dc:continue
   sr=dr*(r1-r0+2);sc=dc*(c1-c0+2)
   j=0
   while 1:
    j+=1
    orr=j*sr;orc=j*sc
    if r0+orr>=R or r1+orr<0 or c0+orc>=C or c1+orc<0:break
    for r,c in P:
     nr=r+orr;nc=c+orc
     if 0<=nr<R and 0<=nc<C:o[nr][nc]=k
 return o
