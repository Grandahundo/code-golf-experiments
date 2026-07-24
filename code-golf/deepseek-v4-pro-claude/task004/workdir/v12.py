p=lambda g:[[R[c-((b:=[*map(any,g),0,0])[r+1]and(b[r+2]or g[r+1][c-1]<1))]for c in range(len(R))]for r,R in enumerate(g)]
