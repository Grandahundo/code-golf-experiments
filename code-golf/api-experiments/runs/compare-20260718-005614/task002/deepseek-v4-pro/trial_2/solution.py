def p(g):r=len(g);c=len(g[0]);g=[l[:]for l in g];q=[(i,j)for i in range(r)for j in range(c)if(i in(0,r-1)or j in(0,c-1))and g[i][j]<1]
 while q:
  i,j=q.pop()
  if g[i][j]<1:g[i][j]=2;q+=[(x,y)for x,y in((i+1,j),(i-1,j),(i,j+1),(i,j-1))if r>x>=0<=y<c and g[x][y]<1]
 return[[{0:4,2:0}.get(v,v)for v in R]for R in g]
