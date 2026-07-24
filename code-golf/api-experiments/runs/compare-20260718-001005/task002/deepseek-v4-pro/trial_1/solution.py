def p(g):
 o=[*map(list,g)]
 for i,r in enumerate(g):
  for j,v in enumerate(r):
   if v<1:
    for p,q in(-1,0),(1,0),(0,-1),(0,1):
     try:x=i+p;y=j+q;while g[x][y]<1:x+=p;y+=q
     except:break
    else:o[i][j]=4
 return o
