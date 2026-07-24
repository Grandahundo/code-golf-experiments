def p(g):
 for r in g:
  for j in range(len(r)-2,-1,-1):
   if r[j]and r[j+1]<1:
    for R in g:
     if R[j]:break
    else:continue
    r[j+1]=r[j];r[j]=0
 return g