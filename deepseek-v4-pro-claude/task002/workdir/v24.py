def p(g):
 m=[[0]*(len(g)+2)]+[[0]+r+[0]for r in g]+[[0]*(len(g)+2)];N=len(m)
 def f(r,c):
  if N>r>=0<=c<N and m[r][c]==0:m[r][c]=-1;f(r+1,c);f(r-1,c);f(r,c+1);f(r,c-1)
 f(0,0)
 return[[(x or 4)*(x>-1)for x in r[1:-1]]for r in m[1:-1]]
