def p(g):
 h=len(g);w=len(g[0])
 o=[[0]*w for _ in range(h)]
 # Group pixels by color
 cols={}
 for r in range(h):
  for c in range(w):
   v=g[r][c]
   if v:
    cols.setdefault(v,[]).append((r,c))
 # Process each color group
 for v in cols:
  px=cols[v]
  mr=max(r for r,c in px)
  # Max column per row (for clamped pixel detection)
  rm={}
  for r,c in px:
   if r not in rm or c>rm[r]: rm[r]=c
  for r,c in px:
   if r==mr: o[r][c]=v
   elif r==mr-1 and (r not in rm or c==rm[r]): o[r][c]=v
   else:
    if c+1<w: o[r][c+1]=v
 return o
