p=lambda g:[[g[r//(h:=len(g))][c//(w:=len(g[0]))]and g[r%h][c%w]for c in range(w*w)]for r in range(h*h)]
