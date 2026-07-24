def p(g):R=range(len(g));m={(i+j)%3:g[i][j]for i in R for j in R if g[i][j]};return[[m[(i+j)%3]for j in R]for i in R]
