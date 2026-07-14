def p(g):
 h=len(g);w=len(g[0])
 o=[[0]*w for _ in range(h)]
 for r in range(h):
  for c in range(w):
   v=g[r][c]
   if v:
    # check below (row r+1)
    nb=r+1>=h or (g[r+1][c]==0 and (c<1 or g[r+1][c-1]==0) and (c+1>=w or g[r+1][c+1]==0))
    # check above (row r-1)
    na=r>0 and (g[r-1][c] or (c>0 and g[r-1][c-1]) or (c+1<w and g[r-1][c+1]))
    # check horizontal neighbor
    hn=(c>0 and g[r][c-1]) or (c+1<w and g[r][c+1])
    # bottom row: nothing below, something above, horizontal neighbor
    if nb and na and hn:
     o[r][c]=v
    # clamped right-diagonal: below exists, right empty, above-left exists
    elif r+1<h and c+1<w and g[r+1][c] and g[r][c+1]==0 and r>0 and c>0 and g[r-1][c-1]:
     o[r][c]=v
    # shift right
    else:
     if c+1<w: o[r][c+1]=v
 return o
