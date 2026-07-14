p=lambda g:[[c*2for c in r]for r in[g[:q]*5for q in(2,3,4)if g[q:]==g[:-q]][0][:9]]
