def p(g):s=g[0].index(5);return[[r[c]*r[c+s+1]*2 for c in range(s)]for r in g]
