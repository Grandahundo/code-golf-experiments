```python
def p(g):
 R=len(g);C=len(g[0])
 v=set();cs=[]
 for i in range(R):
  for j in range(C):
   if g[i][j] and (i,j) not in v:
    c=g[i][j];q=[(i,j)];v.add((i,j));s=[]
    while q:
     r,c1=q.pop();s.append((r,c1))
     for dr,dc in (1,0),(-1,0),(0,1),(0,-1):
      nr,nc=r+dr,c1+dc
      if 0<=nr<R and 0<=nc<C and (nr,nc) not in v and g[nr][nc]==c:
       v.add((nr,nc));q.append((nr,nc))
    cs.append((c,s))
 if not cs:return [[0]*C for _ in range(R)]
 t=max(cs,key=lambda x:len(x[1]))
 tc,tl=t
 Ar=min(r for r,_ in tl);Ac=min(c for _,c in tl)
 Amr=max(r for r,_ in tl);Amc=max(c for _,c in tl)
 Tr={(r-Ar,c-Ac) for r,c in tl}
 mnr=min(r for r,_ in Tr);mxr=max(r for r,_ in Tr)
 mnc=min(c for _,c in Tr);mxc=max(c for _,c in Tr)
 o=[[0]*C for _ in range(R)]
 for r,c in tl:o[r][c]=tc
 for cc,cl in cs:
  if cl==tl:continue
  mr=min(r for r,_ in cl);mc=min(c for _,c in cl)
  br=bc=None
  for tr,tc in Tr:
   r0=mr-tr;c0=mc-tc
   ok=1
   for r,c in cl:
    if (r-r0,c-c0) not in Tr:ok=0;break
   if not ok:continue
   Bmnr=r0+mnr;Bmxr=r0+mxr;Bmnc=c0+mnc;Bmxc=c0+mxc
   ro=max(Ar,Bmnr)<=min(Amr,Bmxr);co=max(Ac,Bmnc)<=min(Amc,Bmxc)
   if ro and co:continue
   rg=cg=-1
   if not ro:
    if Bmxr<Ar:rg=Ar-Bmxr-1
    elif Amr<Bmnr:rg=Bmnr-Amr-1
   if not co:
    if Bmxc<Ac:cg=Ac-Bmxc-1
    elif Amc<Bmnc:cg=Bmnc-Amc-1
   if not ro and not co:
    if rg==1 and cg==1:br,bc=r0,c0;break
   elif not ro and co:
    if rg==1:br,bc=r0,c0;break
   elif not co and ro:
    if cg==1:br,bc=r0,c0;break
  if br is None:continue
  dr=br-Ar;dc=bc-Ac
  k=0
  while 1:
   rc=br+k*dr;ccf=bc+k*dc
   if rc+mxr<0 or rc+mnr>=R or ccf+mxc<0 or ccf+mnc>=C:break
   for tr,tc in Tr:
    rr,ccc=rc+tr,ccf+tc
    if 0<=rr<R and 0<=ccc<C:o[rr][ccc]=cc
   k+=1
 return o
```