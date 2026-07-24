```python
def p(g):
 h,w=len(g),len(g[0])
 nz={(i,j)for i in range(h)for j in range(w)if g[i][j]}
 s={*nz}
 cs=[]
 while s:
  r,c=s.pop()
  v=g[r][c]
  cl=[(r,c)]
  q=[(r,c)]
  while q:
   x,y=q.pop()
   for dx,dy in[(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
    nx,ny=x+dx,y+dy
    if 0<=nx<h and 0<=ny<w and(nx,ny)in s and g[nx][ny]==v:
     s.remove((nx,ny))
     cl.append((nx,ny))
     q.append((nx,ny))
  M=max(c[1]for c in cl)
  rd={}
  for r,c in cl:rd[r]=rd.get(r,[])+[c]
  cs.append((v,M,rd,{*cl}))
 o=[[0]*w for _ in range(h)]
 for v,M,rd,own in cs:
  oth=nz-own
  for r,cw in rd.items():
   occ={*cw}
   bl={c for rr,c in oth if rr==r}|{c for c in occ if c==M}
   for c in sorted(occ,reverse=1):
    if c==M and c in occ:continue
    t=c+1
    if t not in bl and t not in occ:occ.discard(c);occ.add(t)
   for c in occ:o[r][c]=v
 return o
```