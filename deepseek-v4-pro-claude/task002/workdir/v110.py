def p(g):
 H=len(g)+2;g=[[3]*H]+[[3]+[x or 4for x in r]+[3]for r in g]+[[3]*H]
 def f(r,c):
  while 3<g[r][c]:g[r][c]=0;f(r,c+1);f(r,c-1);f(r-1,c);r+=1
 for i in range(1,H-1):f(i,1);f(i,H-2)
 return[r[1:-1]for r in g[1:-1]]
