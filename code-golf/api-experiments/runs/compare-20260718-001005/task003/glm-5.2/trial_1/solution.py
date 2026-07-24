def p(g):
 n=len(g);P=next(P for P in range(1,n+1)if g[:n-P]==g[P:])
 return[[c*2for c in g[i%P]]for i in range(3*n//2)]
