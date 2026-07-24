def p(g):
 n=len(g)+2;a=[[0]*n]+[[0]+[x or 4for x in r]+[0]for r in g]+[[0]*n]
 for k in a*n:
  for r in range(1,n-1):
   for c in range(1,n-1):
    if a[r][c]>3and 0in(a[r-1][c],a[r+1][c],a[r][c-1],a[r][c+1]):a[r][c]=0
 return[r[1:-1]for r in a[1:-1]]
