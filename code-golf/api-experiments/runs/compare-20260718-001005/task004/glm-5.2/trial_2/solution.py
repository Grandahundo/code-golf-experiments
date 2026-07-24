def p(g):
    h=len(g);w=len(g[0]);o=[[0]*w for _ in range(h)]
    for v in range(1,10):
        c=[(r,x) for r in range(h) for x in range(w) if g[r][x]==v]
        if not c:continue
        b=max(r for r,_ in c);m=max(x for _,x in c)
        for r,x in c:o[r][x+(x<m and r<b)]=v
    return o
