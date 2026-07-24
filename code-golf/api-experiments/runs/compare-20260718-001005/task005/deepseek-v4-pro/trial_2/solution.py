def p(g):
 h,w=len(g),len(g[0])
 v=[[0]*w for _ in range(h)]
 cs=[]
 for i in range(h):
  for j in range(w):
   if g[i][j] and not v[i][j]:
    c=g[i][j];q=[(i,j)];p=[]
    while q:
     r,c0=q.pop()
     if 0<=r<h and 0<=c0<w and not v[r][c0] and g[r][c0]==c:
      v[r][c0]=1;p.append((r,c0))
      for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)]:q.append((r+dr,c0+dc))
    mr=min(r for r,_ in p);Mr=max(r for r,_ in p)
    mc=min(c for _,c in p);Mc=max(c for _,c in p)
    cs.append((c,p,(mr,mc,Mr,Mc)))
 anc=max(cs,key=lambda x:len(x[1]))
 o=[[0]*w for _ in range(h)]
 for r,c in anc[1]:o[r][c]=anc[0]
 ac=sum(r for r,_ in anc[1])/len(anc[1])
 ar=sum(c for _,c in anc[1])/len(anc[1])
 for col,pts,(mr,mc,Mr,Mc) in cs:
  if pts==anc[1]:continue
  cr=sum(r for r,_ in pts)/len(pts)
  cc=sum(c for _,c in pts)/len(pts)
  dr=cr-ar;dc=cc-ac
  ds=lambda x:(x>0)-(x<0)
  drs=ds(dr);dcs=ds(dc)
  n=len(pts)
  if n==1:
   r,c=pts[0]
   if abs(dr)>=abs(dc):
    if drs<=0:
     for i in range(r+1):
      if i%4==0:
       for x in(c-1,c,c+1):
        if 0<=i<h and 0<=x<w:o[i][x]=col
      elif i%4!=2:
       if 0<=i<h:o[i][c]=col
    else:
     for i in range(r,h):
      d=i-r
      if d%4==0:
       for x in(c-1,c,c+1):
        if 0<=i<h and 0<=x<w:o[i][x]=col
      elif d%4!=2:
       if 0<=i<h:o[i][c]=col
   else:
    if dcs<=0:
     for j in range(c+1):
      if j%4==0:
       for y in(r-1,r,r+1):
        if 0<=y<h and 0<=j<w:o[y][j]=col
      elif j%4!=2:
       if 0<=j<w:o[r][j]=col
    else:
     for j in range(c,w):
      d=j-c
      if d%4==0:
       for y in(r-1,r,r+1):
        if 0<=y<h and 0<=j<w:o[y][j]=col
      elif d%4!=2:
       if 0<=j<w:o[r][j]=col
  else:
   rows=[r for r,_ in pts];cols=[c for _,c in pts]
   if len(set(rows))==1 or len(set(cols))==1:
    L=n
    if len(set(rows))==1:
     r0=rows[0];c0=mc
     if drs<=0:
      for k in range(L):
       br=r0-k*(L+1)-(L-1)
       for i in range(L):
        for j in range(L):
         if i==0 or i==L-1 or j==0 or j==L-1:
          r=br+i;c=c0+j
          if 0<=r<h and 0<=c<w:o[r][c]=col
     else:
      for k in range(L):
       br=r0+k*(L+1)
       for i in range(L):
        for j in range(L):
         if i==0 or i==L-1 or j==0 or j==L-1:
          r=br+i;c=c0+j
          if 0<=r<h and 0<=c<w:o[r][c]=col
    else:
     r0=mr;c0=cols[0]
     if dcs<=0:
      for k in range(L):
       bc=c0-k*(L+1)-(L-1)
       for i in range(L):
        for j in range(L):
         if i==0 or i==L-1 or j==0 or j==L-1:
          r=r0+i;c=bc+j
          if 0<=r<h and 0<=c<w:o[r][c]=col
     else:
      for k in range(L):
       bc=c0+k*(L+1)
       for i in range(L):
        for j in range(L):
         if i==0 or i==L-1 or j==0 or j==L-1:
          r=r0+i;c=bc+j
          if 0<=r<h and 0<=c<w:o[r][c]=col
   else:
    xc=[(0,0),(0,1),(1,0),(1,2),(2,1),(2,2)]
    if n==3 and Mr-mr==1 and Mc-mc==1:
     offr,offc=mr,mc
    elif n==2 and Mr-mr==1 and Mc-mc==1:
     offr,offc=mr-1,mc
    else:
     offr,offc=mr,mc
    for k in range(n):
     br=offr+k*drs*4
     bc=offc+k*dcs*4
     for dx,dy in xc:
      r=br+dx;c=bc+dy
      if 0<=r<h and 0<=c<w:o[r][c]=col
 return o
