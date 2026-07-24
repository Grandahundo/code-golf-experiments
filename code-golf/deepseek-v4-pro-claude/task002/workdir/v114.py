f=lambda g,r,c,H:H>r>=0<=c<H>3<g[r][c]and(g[r].__setitem__(c,0),f(g,r,c+1,H),f(g,r,c-1,H),f(g,r-1,c,H),f(g,r+1,c,H))
p=lambda g,H=0:[g:=[[x or 4for x in r]for r in g],H:=len(g),[f(g,i,0,H)or f(g,i,~-H,H)for i in range(H)],g][-1]
