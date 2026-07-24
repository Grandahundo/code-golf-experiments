def p(g):
 for i,r in enumerate(g):
  for j in range(len(r)-2,-1,-1):
   if(v:=r[j])and v in g[i+1][j+1:]:r[j:j+2]=0,v
 return g