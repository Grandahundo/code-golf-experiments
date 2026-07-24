def p(g):R=len(g);C=len(g[0]);return[[g[i//R][j//C]and g[i%R][j%C]for j in range(C*C)]for i in range(R*R)]
