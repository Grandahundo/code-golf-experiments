def p(g):
 q=1
 while g[q:]!=g[:-q]:q+=1
 return[[v+(v==1)for v in g[r%q]]for r in range(len(g)*3//2)]
