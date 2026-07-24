def p(g):
 C=len(g[0]);m=[0]*10
 for r in g:
  for j,c in enumerate(r):m[c]=max(m[c],j)
 for r in g:
  for j in range(C)[::-1]:
   if r[j]and j<m[r[j]]and r[j+1]<1:r[j],r[j+1]=0,r[j]
 return g
