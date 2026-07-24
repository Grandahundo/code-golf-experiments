def p(g):
 H=len(g);d={c+r*1j:v or 4for r,o in enumerate(g)for c,v in enumerate(o)}
 def f(z):
  if d.get(z,0)>3:d[z]=0;f(z+1);f(z-1);f(z+1j);f(z-1j)
 for i in range(H):f(i*1j);f(i*1j+~-H)
 return[[d[c+r*1j]for c in range(H)]for r in range(H)]
