def p(g):
 h=len(g);w=len(g[0])
 G=[[0]*(w+2)]+[[0]+r+[0]for r in g]+[[0]*(w+2)]
 o=[[0]*w for _ in range(h)]
 s=set()
 for r in range(h,0,-1):
  for c in range(1,w+1):
   v=G[r][c]
   if v:
    if v in s:
     if G[r+1][c]and not G[r][c+1]:o[r-1][c-1]=v
     else:o[r-1][c]=v
    else:o[r-1][c-1]=v
  s|={c for c in G[r]if c}
 return o
