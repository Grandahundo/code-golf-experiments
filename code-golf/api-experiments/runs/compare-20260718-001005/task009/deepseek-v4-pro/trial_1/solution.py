def p(g):
 R=len(g);C=len(g[0]);M=(R+1)//3;N=(C+1)//3;B=[[g[3*r][3*c]for c in range(N)]for r in range(M)];O=[r[:]for r in B]
 for c in range(N):
  for v in {B[i][c]for i in range(M)}-{0}:
   r=[i for i in range(M)if B[i][c]==v]
   if len(r)>1:
    for i in range(min(r),max(r)+1):O[i][c]=v
 for r in range(M):
  for v in set(B[r])-{0}:
   c=[i for i,x in enumerate(B[r])if x==v]
   if len(c)>1:
    for j in range(min(c),max(c)+1):O[r][j]=v
 S=g[2][0];o=[[S if i%3==2 or j%3==2 else 0 for j in range(C)]for i in range(R)]
 for r in range(M):
  for c in range(N):
   v=O[r][c]
   if v:o[3*r][3*c]=o[3*r][3*c+1]=o[3*r+1][3*c]=o[3*r+1][3*c+1]=v
 return o
