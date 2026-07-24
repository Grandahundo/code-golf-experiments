def p(g):d={(i+j)%(L:=len({*sum(g,[])}-{0})):v for i,r in enumerate(g)for j,v in enumerate(r)if v};return[[d[(i+j)%L]for j in range(len(r))]for i,r in enumerate(g)]
