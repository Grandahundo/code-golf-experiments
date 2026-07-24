def p(g):
 L=g[2][2];N=(len(g)+1)//3;M=(len(g[0])+1)//3
 c=[[g[i*3][j*3]for j in range(M)]for i in range(N)]
 r=[x[:]for x in c]
 for d in set(sum(c,[]))-{0,L}:
  P=[(i,j)for i in range(N)for j in range(M)if c[i][j]==d]
  R={};C={}
  for i,j in P:R[i]=R.get(i,[])+[j];C[j]=C.get(j,[])+[i]
  for i,js in R.items():
   if len(js)-1:a,b=min(js),max(js);r[i][a:b+1]=[d]*(b-a+1)
  for j,ir in C.items():
   if len(ir)-1:
    a,b=min(ir),max(ir)
    for i in range(a,b+1):r[i][j]=d
 o=[x[:]for x in g]
 for i in range(N):
  for j in range(M):o[i*3][j*3:j*3+2]=o[i*3+1][j*3:j*3+2]=[r[i][j]]*2
 return o
