p=lambda g:[[g[i//n][j//n]and g[i%n][j%n]for j in range(n*n)]for i in range((n:=len(g))*n)]
