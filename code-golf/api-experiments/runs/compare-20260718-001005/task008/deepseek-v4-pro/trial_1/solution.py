def p(g):
 R=range;h=len(g);w=len(g[0])
 t=[(r,c)for r in R(h)for c in R(w)if g[r][c]==2]
 u=[(r,c)for r in R(h)for c in R(w)if g[r][c]==8]
 r2,c2=zip(*t);r8,c8=zip(*u)
 a,b,c,d=min(r2),max(r2),min(c2),max(c2)
 e,f,g,h=min(r8),max(r8),min(c8),max(c8)
 dx=(d<g)*(g-d-1)-(c>h)*(c-h-1)
 dy=(b<e)*(e-b-1)-(a>f)*(a-f-1)
 o=[w*[0]for _ in g]
 for r,c in u:o[r][c]=8
 for r,c in t:o[r+dy][c+dx]=2
 return o
