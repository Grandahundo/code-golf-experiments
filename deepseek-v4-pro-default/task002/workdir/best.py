def p(g,i=0,j=0):
 for d in(-1,1)*(i<len(g)>j<99>g[i][j]<1):g[i][j]=12;p(g,i-d,j);p(g,i,j-d)
 return[[4-x/3for x in r]for r in g]