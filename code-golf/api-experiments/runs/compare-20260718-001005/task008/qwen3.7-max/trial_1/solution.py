def p(g):
 H=len(g);W=len(g[0])
 def B(v):
  r,c=zip(*[(r,c)for r in range(H)for c in range(W)if g[r][c]==v])
  return min(r),max(r),min(c),max(c)
 a,b,c,d=B(2);e,f,h,i=B(8)
 x=y=0;Ho=c<=i and h<=d;Vo=a<=f and e<=b
 if Ho and not Vo:x=(e-1-b)if b<e else f+1-a
 if Vo and not Ho:y=(h-1-d)if d<h else i+1-c
 o=[[0]*W for _ in range(H)]
 for r in range(H):
  for c in range(W):
   v=g[r][c]
   if v:o[r+x*(v==2)][c+y*(v==2)]=v
 return o
