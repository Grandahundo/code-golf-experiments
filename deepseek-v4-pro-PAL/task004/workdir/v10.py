def p(g):
 h=len(g)
 for r in range(h):
  if r+1<h and any(g[r+1]):g[r]=[0]+g[r][:-1]
 return g
