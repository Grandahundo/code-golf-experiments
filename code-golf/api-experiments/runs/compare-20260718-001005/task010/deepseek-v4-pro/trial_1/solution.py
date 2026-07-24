def p(g):t=[c.index(5)if 5 in c else len(g)for c in zip(*g)];return[[v//5*sum((t[k],k)<=(t[j],j)for k in range(len(t)))for j,v in enumerate(r)]for r in g]
