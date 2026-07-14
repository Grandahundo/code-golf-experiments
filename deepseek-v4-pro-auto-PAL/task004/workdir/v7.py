def p(g):
 b=[any(r)for r in g]+[0,0];W=len(g[0])
 return[[max(R)*(j in{c+(b[i+1]and(b[i+2]or g[i+1][c]<1))for c,x in enumerate(R)if x})for j in range(W)]for i,R in enumerate(g)]
