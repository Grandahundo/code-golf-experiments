def p(g):
 n=len(g)+2;a=[[4]*n]+[[4]+[x or 4for x in r]+[4]for r in g]+[[4]*n]
 def f(r,c):
  if n>r>=0<=c<n>3<a[r][c]:a[r][c]=0;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
 f(0,0)
 return[r[1:-1]for r in a[1:-1]]
