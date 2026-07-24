def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 for i in range(h):
  for j in range(w):
   if g[i][j] and o[i][j]==0:
    d=g[i][j];c=[]
    def f(i,j):
     if(0<=i<h)&(0<=j<w)&(g[i][j]==d)&(o[i][j]==0):
      o[i][j]=-1;c+=[(i,j)]
      f(i+1,j);f(i-1,j);f(i,j+1);f(i,j-1)
    f(i,j)
    mr,mc=map(max,zip(*c))
    for x,y in c:o[x][min(y+(x!=mr),mc)]=d
 return o
