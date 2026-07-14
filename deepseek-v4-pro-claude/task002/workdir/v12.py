def p(g,f=lambda g,r,c:H>r>=0<=c<W and g[r][c]==0and(g[r].__setitem__(c,-1),f(g,r+1,c),f(g,r-1,c),f(g,r,c+1),f(g,r,c-1))):
 global H,W;H=len(g);W=len(g[0])
 for i in range(H):f(g,i,0);f(g,i,W-1)
 for i in range(W):f(g,0,i);f(g,H-1,i)
 return[[(x or 4)*(x>-1)for x in r]for r in g]
