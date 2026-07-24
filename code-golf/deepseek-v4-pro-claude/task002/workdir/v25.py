def p(g):
 H=len(g);s=[(i,j)for i in range(H)for j in range(H)if i%(H-1)*(j%(H-1))<1>=g[i][j]]
 while s:
  r,c=s.pop();g[r][c]=-1
  s+=[(a,b)for a,b in((r+1,c),(r-1,c),(r,c+1),(r,c-1))if H>a>=0<=b<H>0==g[a][b]]
 return[[(x or 4)*(x>-1)for x in r]for r in g]
