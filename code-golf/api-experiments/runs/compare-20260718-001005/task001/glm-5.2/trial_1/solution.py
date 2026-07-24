def p(g):n=len(g);return[[g[i//n][j//n]and g[i%n][j%n]for j in range(n*n)]for i in range(n*n)]
