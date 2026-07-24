def p(g):
 H=len(g);W=len(g[0]);o=[r[:]for r in g]
 def f(r,c):
  if H>r>=0<=c<W and o[r][c]==0:o[r][c]=-1;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
 for i in range(H):f(i,0);f(i,W-1)
 for i in range(W):f(0,i);f(H-1,i)
 return[[(x or 4)*(x>-1)for x in r]for r in o]
