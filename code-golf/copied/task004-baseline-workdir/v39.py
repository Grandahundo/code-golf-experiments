def p(g):
 for r,s in zip(g,g[1:]):
  for j,v in[*enumerate(r)][::-1]:
   if v*(v in s[j+1:]):r[j:j+2]=0,v
 return g