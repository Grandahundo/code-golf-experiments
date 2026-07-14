def p(g):
 H=len(g);W=len(g[0]);o=[r[:]for r in g]
 def f(r,c):
  if H>r>=0<=c<W>0==o[r][c]:o[r][c]=-1;[f(r+a,c+b)for a,b in((1,0),(-1,0),(0,1),(0,-1))]
 for i in range(H):
  for j in range(W):
   if i%(H-1)*(j%(W-1))<1:f(i,j)
 return[[(x or 4)*(x>-1)for x in r]for r in o]
