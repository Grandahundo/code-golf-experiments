def p(g):
 P=1
 while g[P:]!=g[:-P]:P+=1
 return[[x*2for x in g[i%P]]for i in range(len(g)*3//2)]
