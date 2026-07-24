def p(g):L=len({*sum(g,[])}-{0});d={(i+j)%L:v for i,r in enumerate(g) for j,v in enumerate(r) if v};return[[d[(i+j)%L]for j in range(len(r))]for i,r in enumerate(g)]
