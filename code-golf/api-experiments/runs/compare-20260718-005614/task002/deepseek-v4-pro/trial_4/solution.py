def p(g):
 h,w=len(g),len(g[0]);o=[*map(list,g)]
 def f(r,c):
  if h>r>=0<=c<w and o[r][c]<1:o[r][c]=1;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
 for r in range(h):f(r,0);f(r,w-1)
 for c in range(w):f(0,c);f(h-1,c)
 return[[{0:4,1:0}.get(o[r][c],o[r][c])for c in range(w)]for r in range(h)]
