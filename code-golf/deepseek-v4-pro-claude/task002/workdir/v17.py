def p(g):
 H=len(g)
 def f(r,c):
  try:
   if g[r][c]==0<=r and c>=0:g[r][c]=-1;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
  except:0
 for i in range(H):f(i,0);f(i,H-1);f(0,i);f(H-1,i)
 return[[(x or 4)*(x>-1)for x in r]for r in g]
