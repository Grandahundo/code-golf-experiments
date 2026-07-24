p=lambda g:[*map(list,zip(*[[c[i%next(p for p in range(1,-~len(c))if c[:-p]==c[p:])]*2for i in range(len(g)+3)]for c in zip(*g)]))]
