def p(g):
 a=[any(r)for r in g]+[0];W=len(g[0])
 return[[max(R)*(j in{c+(a[i+1]and g[i+1][c-1]<1)for c,x in enumerate(R)if x})for j in range(W)]for i,R in enumerate(g)]
