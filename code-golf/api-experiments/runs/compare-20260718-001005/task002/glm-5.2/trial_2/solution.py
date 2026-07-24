def p(g):
 g=[r[:]for r in g];h=len(g);w=len(g[0])
 s=[(i,j)for i in range(h)for j in range(w)if(i<1or j<1or i>h-2or j>w-2)and g[i][j]<1]
 for i,j in s:g[i][j]=-1
 while s:
  i,j=s.pop()
  for a,b in(1,0),(-1,0),(0,1),(0,-1):
   x,y=i+a,j+b
   if 0<=x<h and 0<=y<w and g[x][y]<1:g[x][y]=-1;s.append((x,y))
 return[[0if c<0else 4if c<1else c for c in r]for r in g]
