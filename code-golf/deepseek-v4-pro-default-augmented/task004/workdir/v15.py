def p(g):
 w=len(g[0]);o=[[0]*w for _ in g]
 for v in{*sum(g,[])}-{0}:
  P=[(r,c)for r,R in enumerate(g)for c,x in enumerate(R)if x==v]
  r=P[0][0];b=P[-1][0];c=P[0][1];t=b-r+1;W=P[-1][1]-c+1
  for i in range(W-t+2):o[r][c+i+1]=o[b][c+i+t-2]=v
  for i in range(1,t-1):o[r+i][c+i]=o[r+i][min(c+i+W-t+2,c+W-1)]=v
 return o
