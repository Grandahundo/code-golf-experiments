def p(g):
 R=range;D=-4,4,0
 S=max(([(i+a,j+c)for a in R(3)for c in R(3)if g[i+a][j+c]]for i in R(19)for j in R(19)),key=len)
 o={(Y+k*r,X+k*d):max(g[Y+r][X+d]for Y,X in S)for r in D for d in D for k in R(8)for Y,X in S}
 return[[o.get((i,j),0)for j in R(21)]for i in R(21)]
