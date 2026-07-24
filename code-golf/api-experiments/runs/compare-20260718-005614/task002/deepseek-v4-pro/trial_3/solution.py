def p(g):
	h=len(g);w=len(g[0]);r=range
	def f(i,j):
		if not(h>i>=0<=j<w)or g[i][j]:return
		g[i][j]=2
		for ni,nj in(i+1,j),(i-1,j),(i,j+1),(i,j-1):f(ni,nj)
	for i in r(h):f(i,0);f(i,w-1)
	for j in r(1,w-1):f(0,j);f(h-1,j)
	for i in g:i[:]=[x<1 and 4or x==2 and 0or x for x in i]
	return g
