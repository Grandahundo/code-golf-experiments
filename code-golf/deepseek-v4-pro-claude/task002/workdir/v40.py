def p(g):
 H=len(g);d={c+1j*r:v for r,o in enumerate(g)for c,v in enumerate(o)};W=(1,-1,1j,-1j)
 def f(z):
  if d.get(z)==0:d[z]=-1;[f(z+w)for w in W]
 [f(z)for z in[*d]if any(z+w not in d for w in W)]
 return[[(d[c+1j*r]or 4)*(d[c+1j*r]>-1)for c in range(H)]for r in range(H)]
