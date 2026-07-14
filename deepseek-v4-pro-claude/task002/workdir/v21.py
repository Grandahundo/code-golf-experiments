def p(g):
 N=len(g)+2;m=[[0]*N]+[[0]+r+[0]for r in g]+[[0]*N]
 def f(r,c):
  try:
   if m[r][c]==0:m[r][c]=-1;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
  except:0
 f(0,0)
 return[[(x or 4)*(x>-1)for x in r[1:-1]]for r in m[1:-1]]
