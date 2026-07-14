def p(g):
 S=len(g)
 # Find densest 3x3 window - this is the middle block
 best=0
 mid=(0,0)
 for r in range(S-2):
  for c in range(S-2):
   d=sum(1 for i in range(3) for j in range(3) if g[r+i][c+j])
   if d>best:best=d;mid=(r,c)
 mr,mc=mid
 # Sprite pattern from middle block
 P=[(i,j) for i in range(3) for j in range(3) if g[mr+i][mc+j]]
 # Build output: for each valid block anchor, stamp along direction
 o=[[0]*S for _ in range(S)]
 for r in range(S-2):
  for c in range(S-2):
   if (r-mr)%4==0 and (c-mc)%4==0:
    v=0
    for i in range(3):
     for j in range(3):
      if g[r+i][c+j]:v=g[r+i][c+j];break
     if v:break
    if v:
     dr=(r-mr)//4;dc=(c-mc)//4
     R,C=r,c
     while 0<=R<S and 0<=C<S:
      for i,j in P:
       nr,nc=R+i,C+j
       if 0<=nr<S and 0<=nc<S:o[nr][nc]=v
      if dr==0 and dc==0:break
      R+=dr*4;C+=dc*4
 return o
