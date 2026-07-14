def p(g):
 n=len(g)+2;g=[[-1]*n]+[[-1]+r+[-1]for r in g]+[[-1]*n]
 for k in g*n:
  for r in range(1,n-1):
   for c in range(1,n-1):
    if g[r][c]<1and-1in(g[r-1][c],g[r+1][c],g[r][c-1],g[r][c+1]):g[r][c]=-1
 return[[(x or 4)*(x>-1)for x in r[1:-1]]for r in g[1:-1]]
