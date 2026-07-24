def p(g):
 h=len(g);p=1
 while any(g[i]!=g[i+p]for i in range(h-p)):p+=1
 return[[c*2for c in g[i%p]]for i in range(h*3//2)]
