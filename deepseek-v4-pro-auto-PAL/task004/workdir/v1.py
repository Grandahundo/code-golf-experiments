def p(g):
  H=len(g);W=len(g[0])
  bl=[all(x==0 for x in row) for row in g]+[1,1]
  out=[[0]*W for _ in range(H)]
  for r in range(H):
    rm=max((c for c in range(W) if g[r][c]),default=-1)
    for c in range(W):
      x=g[r][c]
      if x:
        bot = bl[r+1]
        clamp = (not bl[r+1]) and bl[r+2] and c==rm
        if bot or clamp: out[r][c]=x
        elif c+1<W: out[r][c+1]=x
  return out
