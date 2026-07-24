```python
def p(g):
 r=range;R,C=len(g),len(g[0])
 T=[(i,j)for i in r(R)for j in r(C)if g[i][j]==2]
 E=[(i,j)for i in r(R)for j in r(C)if g[i][j]==8]
 a1,b1=map(min,zip(*T));a2,b2=map(max,zip(*T))
 c1,d1=map(min,zip(*E));c2,d2=map(max,zip(*E))
 u=v=0
 if b2<d1:v=d1-b2-1
 elif b1>d2:v=d2-b1+1
 elif a2<c1:u=c1-a2-1
 elif a1>c2:u=c2-a1+1
 o=[[0]*C for _ in r(R)]
 for i,j in E:o[i][j]=8
 for i,j in T:o[i+u][j+v]=2
 return o
```