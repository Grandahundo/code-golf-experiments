def p(g,r=0):
 h=len(g);w=len(g[0])
 if r>=h:return[[0]*w for _ in g]
 o=p(g,r+1);e=r+1==h or any(g[r+1])<1
 for c in range(w):
  if g[r][c]:o[r][c+1-((c>0<g[r][c-1]or c+1<w>g[r][c+1])and e or r+1<h and g[r+1][c]*o[r+1][c]>0)]=g[r][c]
 return o
