def p(g):
 h=len(g);w=len(g[0]);v=[[0]*w for _ in range(h)];q=[]
 for i in range(h):
  for j in range(w):
   if(i in(0,h-1)or j in(0,w-1))and g[i][j]<1:v[i][j]=1;q.append((i,j))
 for i,j in q:
  for a,b in(-1,0),(1,0),(0,-1),(0,1):
   x,y=i+a,j+b
   if 0<=x<h and 0<=y<w and g[x][y]<1 and not v[x][y]:v[x][y]=1;q.append((x,y))
 return[[4 if g[i][j]<1 and not v[i][j]else g[i][j]for j in range(w)]for i in range(h)]
