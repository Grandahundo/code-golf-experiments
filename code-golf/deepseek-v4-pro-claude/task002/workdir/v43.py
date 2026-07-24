def p(g):
 n=len(g)+2;a=[[4]*n]+[[4]+[x or 4for x in r]+[4]for r in g]+[[4]*n]
 def f(r,c):
  if 3<a[r][c]:a[r][c]=0;[f(r+i,c+j)for i,j in((1,0),(-1,0),(0,1),(0,-1))]
 f(0,0)
 return[r[1:-1]for r in a[1:-1]]
