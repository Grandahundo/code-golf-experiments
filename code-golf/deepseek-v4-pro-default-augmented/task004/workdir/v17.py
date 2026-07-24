def p(g):
 o=[[0for _ in r]for r in g]
 for r,R in enumerate(g):
  for c,v in enumerate(R):
   if v:a=r and v in g[r-1];b=r<len(g)-1 and v in g[r+1];o[r][c+(a<1or b&g[r+1][c]!=v)]=v
 return o
