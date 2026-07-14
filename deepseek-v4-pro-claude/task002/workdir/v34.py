def p(g):
 g=[[0]*-~-~len(g)]+[[0]+r+[0]for r in g]+[[0]*-~-~len(g)]
 def f(r,c):
  try:
   if r>=0<=c and g[r][c]==0:g[r][c]=5;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
  except:0
 f(0,0)
 return[[(x<5)*(x or 4)for x in r[1:-1]]for r in g[1:-1]]
