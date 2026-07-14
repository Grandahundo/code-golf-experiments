def p(g):
 H=len(g);d={(r,c):v or 4for r,o in enumerate(g)for c,v in enumerate(o)}
 def f(z):
  if d.get(z,0)>3:d[z]=0;[f((z[0]+a,z[1]+b))for a,b in((1,0),(-1,0),(0,1),(0,-1))]
 [f(k)for k in list(d)if 0in k or H-1in k]
 return[[d[r,c]for c in range(H)]for r in range(H)]
