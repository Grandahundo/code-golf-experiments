def p(g):
 H=len(g);a=[[x or 4for x in r]+[3]for r in g]+[[3]*-~H]
 def f(r,c):
  while a[r][c]>3:a[r][c]=0;f(r,c+1);f(r,c-1);f(r-1,c);r+=1
 f(0,0);f(~-H,~-H)
 return[r[:H]for r in a[:H]]
