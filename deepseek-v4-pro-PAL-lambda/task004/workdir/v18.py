def p(g):
 h,w=len(g),len(g[0]);m={g[r][c]:r for r in range(h)for c in range(w)if g[r][c]};o=[[0]*w for _ in[0]*h]
 for r in range(h):
  for c in range(w):
   if g[r][c]:o[r][c+(r!=m[g[r][c]]and(g[r+1][c]<1 or c+1<w and g[r][c+1]>0))]=g[r][c]
 return o
