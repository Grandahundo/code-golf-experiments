p=lambda g:[(g[:q]*5)[:9]for q in range(6)if g[q:]==g[:-q]][0]and[[c*2for c in r]for r in(g[:min(q for q in range(6)if g[q:]==g[:-q])]*5)[:9]]
