```python
def p(g):
 t,E=[[(i,j)for i,r in enumerate(g)for j,v in enumerate(r)if v==x]for x in(2,8)]
 (r2,c2),(r8,c8)=zip(*t),zip(*E)
 a,b,c,d=min(r2),max(r2),min(c2),max(c2)
 e,f,g,h=min(r8),max(r8),min(c8),max(c8)
 dx=dy=0
 if c<=h and g<=d:dx,dy=0,(e-b-1)if e>b else(f-a+1)
 elif a<=f and e<=b:dx,dy=(g-d-1)if g>d else(h-c+1),0
 o=[[0]*len(g[0])for _ in g]
 for r,c in E:o[r][c]=8
 for r,c in t:o[r+dy][c+dx]=2
 return o
```