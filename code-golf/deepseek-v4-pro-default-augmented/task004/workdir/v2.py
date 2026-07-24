def p(g):
 o=[[0]*len(g[0])for _ in g]
 for r,R in enumerate(g):
  for c,v in enumerate(R):
   if v:a=r and v in g[r-1];b=r<len(g)-1 and v in g[r+1];o[r][c+(a<1 or b and g[r+1][c]!=v)]=v
 return o
