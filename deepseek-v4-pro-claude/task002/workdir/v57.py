def p(g):
 n=len(g)+2;a=[[-1]*n]+[[-1]+r+[-1]for r in g]+[[-1]*n]
 for k in a*n:
  for r in range(1,n):
   for c in range(1,n):
    if a[r][c]==0and-1in(a[r-1][c],a[r+1][c],a[r][c-1],a[r][c+1]):a[r][c]=-1
 return[[(x or 4)*(x>-1)for x in r[1:-1]]for r in a[1:-1]]
