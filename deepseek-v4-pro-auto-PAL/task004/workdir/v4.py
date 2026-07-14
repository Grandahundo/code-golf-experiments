def p(g):
 b=[any(r)for r in g]+[0,0]
 s=lambda r,c:b[r+1]and(b[r+2]or g[r+1][c]<1)
 return[[g[r][c]*(s(r,c)<1)or c and g[r][c-1]*s(r,c-1)for c in range(len(R))]for r,R in enumerate(g)]
