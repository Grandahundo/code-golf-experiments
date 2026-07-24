def p(g):
 n=len(g);g=[[0]*-~-~n]+[[0]+r+[0]for r in g]+[[0]*-~-~n]
 def f(r,c):
  if g[r][c]==0:
   g[r][c]=5
   for a,b in((r+1,c),(r-1,c),(r,c+1),(r,c-1)):
    if 0<=a<=n<=n and 0<=b:f(a,b)
 f(0,0)
