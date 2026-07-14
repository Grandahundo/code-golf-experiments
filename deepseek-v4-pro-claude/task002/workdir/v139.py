def p(g):
 d={c+1j*r:v or 4for r,o in enumerate(g)for c,v in enumerate(o)}
 def f(z):
  while d.get(z,0)>3:d[z]=0;f(z+1);f(z-1);f(z-1j);z+=1j
 H=len(g);f(0);f(~-H+~-H*1j)
 return[[d[c+1j*r]for c in range(H)]for r in range(H)]
