```python
def p(g):
 R=len(g);C=len(g[0]);o=[[0]*C for _ in range(R)]
 p2=[(r,c) for r in range(R) for c in range(C) if g[r][c]==2]
 p8=[(r,c) for r in range(R) for c in range(C) if g[r][c]==8]
 a=lambda l:(min(l),max(l))
 R2=a([r for r,c in p2]);C2=a([c for r,c in p2])
 R8=a([r for r,c in p8]);C8=a([c for r,c in p8])
 dr=sum(R2)-sum(R8);dc=sum(C2)-sum(C8)
 for r,c in p8:o[r][c]=8
 if abs(dr)>=abs(dc):
  s=(R8[0]-1-(R2[1]-R2[0]) if dr<0 else R8[1]+1)-R2[0]
  for r,c in p2:o[r+s][c]=2
 else:
  s=(C8[0]-1-(C2[1]-C2[0]) if dc<0 else C8[1]+1)-C2[0]
  for r,c in p2:o[r][c+s]=2
 return o
```