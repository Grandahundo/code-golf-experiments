def p(g):
 m={};E=enumerate
 for R in g:
  for c,v in E(R):
   if v==5:m[c]=m.get(c,len(m)+1)
 return[[v==5 and m[c]or 0 for c,v in E(R)]for R in g]
