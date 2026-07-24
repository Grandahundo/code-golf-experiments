def p(g):h=len(g);return[*map(list,zip(*[[c[i%min(l for l in range(1,h+1)if all(c[i]==c[i%l]for i in range(h)))]*2for i in range(h+3)]for c in zip(*g)]))]
