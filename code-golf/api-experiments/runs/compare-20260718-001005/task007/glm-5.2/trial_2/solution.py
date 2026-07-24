def p(g):
 m={(r+c)%3:v for r,x in enumerate(g)for c,v in enumerate(x)if v}
 return[[m[(r+c)%3]for c,_ in enumerate(g[0])]for r,_ in enumerate(g)]
