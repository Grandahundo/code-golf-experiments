def p(g):
 H=len(g);a=sum([[x or 4for x in r]for r in g],[])
 def f(i):
  while 0<=i<H*H and a[i]>3and(i%H or 1):a[i]=0;f(i+H);f(i-H);f(i+1);f(i-1)
 f(0);f(H*H-1)
 return[a[i*H:i*H+H]for i in range(H)]
