def p(g,r=0):
 if r>=len(g):return[[0]*len(g[0])for _ in g]
 o=p(g,r+1);e=r+1==len(g)or any(g[r+1])<1
 for c in range(len(g[0])):
  if g[r][c]:o[r][c+1-((c>0<g[r][c-1]or c+1<len(g[0])>g[r][c+1])and e or r+1<len(g)and g[r+1][c]*o[r+1][c]>0)]=g[r][c]
 return o
