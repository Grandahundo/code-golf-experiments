def p(g):
 g=[[x or 4for x in r]for r in g]
 def f(i,j):
  if(r:=g[i%N])[j%N]>3:
   for d in-1,1:r[j%N]=0;f(i+d,j);f(i,j+d)
 for i in range(N:=len(g)):f(0,i);f(-1,i);f(i,0);f(i,-1)
 return g