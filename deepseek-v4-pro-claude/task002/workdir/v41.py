def p(g):
 n=len(g)+2;a=[[0]*n]+[[0]+r+[0]for r in g]+[[0]*n]
 def f(r,c):
  if n>r>=0<=c<n>0==a[r][c]:a[r][c]=-1;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
 f(0,0)
 return[[(x or 4)*(x>-1)for x in r[1:-1]]for r in a[1:-1]]
