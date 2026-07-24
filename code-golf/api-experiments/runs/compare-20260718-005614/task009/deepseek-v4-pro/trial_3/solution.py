def p(g):
 D=g[2][2]
 R,C=len(g),len(g[0])
 A=[i for i,r in enumerate(g) if all(v==D for v in r)]
 B=[j for j in range(C) if all(g[i][j]==D for i in range(R))]
 S=list(zip([0]+[x+1 for x in A],A+[R]))
 T=list(zip([0]+[y+1 for y in B],B+[C]))
 M=[[g[r][c] for c,_ in T] for r,_ in S]
 for row in M:
  for d in{*row}-{0}:
   i=[j for j,v in enumerate(row) if v==d]
   if len(i)>1:l,h=min(i),max(i);row[l:h+1]=[d]*(h-l+1)
 for j in range(len(T)):
  col=[row[j] for row in M]
  for d in{*col}-{0}:
   i=[k for k,v in enumerate(col) if v==d]
   if len(i)>1:
    l,h=min(i),max(i)
    for k in range(l,h+1):M[k][j]=d
 O=[r.copy() for r in g]
 for i,(rs,re) in enumerate(S):
  for j,(cs,ce) in enumerate(T):
   v=M[i][j]
   for r in range(rs,re):O[r][cs:ce]=[v]*(ce-cs)
 return O
