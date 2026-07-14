def p(g):
 b=[any(r)for r in g]+[0,0]
 o=[R if not b[i+1]else[0]+R[:-1]for i,R in enumerate(g)]
 for i,R in enumerate(g):
  if b[i+1]>b[i+2]:
   m=max(c for c,x in enumerate(g[i+1])if x);o[i][m]=max(R);o[i][m+1]=0
 return o
