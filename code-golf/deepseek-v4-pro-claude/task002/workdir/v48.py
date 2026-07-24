def p(g):
 a=[[4]*(len(g)+2)]+[[4]+[x or 4for x in r]+[4]for r in g]+[[4]*(len(g)+2)]
 def f(r,c):
  if a[r][c]>3:a[r][c]=0;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
 f(0,0)
 return[r[1:-1]for r in a[1:-1]]
