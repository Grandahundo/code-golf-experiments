def p(g):
 b=[any(r)for r in g]+[0,0]
 return[[R[c-1]if b[r+1]and(b[r+2]or g[r+1][c-1]<1)else x for c,x in enumerate(R)]for r,R in enumerate(g)]
