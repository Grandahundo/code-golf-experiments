def p(g,m=0):
 for r,s in zip(g,g[1:]):
  for j,v in[*enumerate(r)][::-1]:v*(v in s[j+1:])and r.__setitem__(slice(j,j+2),(0,v))
 return g