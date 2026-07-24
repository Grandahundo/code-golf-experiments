def p(g):
 h=len(g);w=len(g[0]);o=[w*[0]for _ in g];i=1;s=[]
 for x in range(h):
  for j in range(w):
   if g[x][j]==5and j not in s:
    for k in range(x,h):o[k][j]=i
    i+=1;s+=j,
 return o
