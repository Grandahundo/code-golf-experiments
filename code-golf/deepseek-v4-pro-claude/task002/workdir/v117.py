def p(g):
 H=len(g);W={(r,c)for r in range(H)for c in range(H)if g[r][c]<1};o={(r,c)for r,c in W if 0in(r,c,r-~-H,c-~-H)}
 while 1:
  n={(r+a,c+b)for r,c in o for a,b in((1,0),(-1,0),(0,1),(0,-1))}&W-o
  if not n:break
  o|=n
 return[[4*((r,c)in W-o)or g[r][c]for c in range(H)]for r in range(H)]
