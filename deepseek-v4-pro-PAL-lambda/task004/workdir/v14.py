def p(g):
 h,w=len(g),len(g[0])
 G=[[0]*(w+2)]+[[0]+r+[0]for r in g]+[[0]*(w+2)]
 o=[[0]*w for _ in range(h)]
 for r in range(1,h+1):
  R=G[r];A=G[r-1];B=G[r+1]
  for c in range(1,w+1):
   v=R[c]
   if v:
    if not(B[c-1]or B[c]or B[c+1])and v in A:o[r-1][c-1]=v
    elif B[c]and not R[c+1]:o[r-1][c-1]=v
    else:o[r-1][c]=v
 return o
