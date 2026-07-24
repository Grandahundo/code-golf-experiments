p=lambda g:[[[c*2for c in r]for r in g[:q]]*5for q in range(6)if g[q:]==g[:-q]][0][:9]
