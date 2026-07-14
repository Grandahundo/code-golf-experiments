def p(g):
 H=len(g);o=[r[:]for r in g]
 s=[(r,c)for r in range(H)for c in range(len(g[0]))if o[r][c]<1 and(r*c==0 or r==H-1 or c==len(g[0])-1)]
 R={}
 for r,c in s:R[r,c]=1
 while s:
  r,c=s.pop()
  for a,b in((1,0),(-1,0),(0,1),(0,-1)):
   n=(r+a,c+b)
   if 0<=n[0]<H and 0<=n[1]<len(g[0]) and o[n[0]][n[1]]<1 and n not in R:R[n]=1;s+=[n]
 return[[4*((r,c)not in R)*(o[r][c]<1)or o[r][c] for c in range(len(g[0]))]for r in range(H)]
