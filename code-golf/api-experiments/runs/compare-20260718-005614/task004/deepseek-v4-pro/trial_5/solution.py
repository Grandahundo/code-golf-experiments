def p(g):
 h,w=len(g),len(g[0]);c=[[*r]for r in g];o=[[0]*w for _ in c]
 for i,r in enumerate(c):
  for j,v in enumerate(r):
   if v:
    q=[(i,j)];r[j]=0;l=[];mr=i;mc=j
    while q:
     r0,c0=q.pop();l.append((r0,c0));mr=max(mr,r0);mc=max(mc,c0)
     for dr in(-1,0,1):
      for dc in(-1,0,1):
       if dr|dc:
        nr,nc=r0+dr,c0+dc
        if 0<=nr<h and 0<=nc<w and c[nr][nc]==v:c[nr][nc]=0;q.append((nr,nc))
    for r0,c0 in l:o[r0][c0+(r0!=mr and c0<mc)]=v
 return o
