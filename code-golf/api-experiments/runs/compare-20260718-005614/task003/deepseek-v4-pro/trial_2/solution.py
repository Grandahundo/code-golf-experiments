p=lambda g:[[x*2 for x in g[i%[l for l in range(1,7)if g[:-l]==g[l:]][0]]]for i in range(9)]
