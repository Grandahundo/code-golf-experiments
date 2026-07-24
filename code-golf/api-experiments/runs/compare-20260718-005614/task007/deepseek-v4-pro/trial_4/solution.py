def p(g,e=enumerate):s={(i+j)%3:v for i,r in e(g)for j,v in e(r)if v};return[[s[(i+j)%3]for j in range(len(r))]for i,r in e(g)]
