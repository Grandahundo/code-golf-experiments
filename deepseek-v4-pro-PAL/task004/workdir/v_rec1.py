def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 R=lambda c,r,s:c<w and(r>=0 and(g[r][c]and(s:=s|(c>0<g[r][c-1]or c+1<w>g[r][c+1])and(r+1==h or any(g[r+1])<1),o[r].__setitem__(c+1-s,g[r][c]),R(c,r-1,s))[-1]or R(c,r-1,0))or R(c+1,h-1,0))
 R(0,h-1,0)
 return o
