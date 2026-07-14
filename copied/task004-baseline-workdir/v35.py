def p(g):
 for r,s in zip(g,g[1:]):
  for j in range(len(r)-2,-1,-1):
   if(v:=r[j])*(v in s[j+1:]):r[j:j+2]=0,v
 return g