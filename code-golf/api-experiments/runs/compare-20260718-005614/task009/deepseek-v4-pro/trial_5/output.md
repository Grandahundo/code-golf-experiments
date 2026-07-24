```python
def p(g):
 h,w=len(g),len(g[0]);L=g[0][2];R=(h+1)//3;C=(w+1)//3
 o=[[g[3*i][3*j]for j in range(C)]for i in range(R)]
 c=[r[:]for r in o]
 for d in{*sum(o,[])}-{0,L}:
  for i in range(R):
   J=[j for j in range(C)if o[i][j]==d]
   if J:a,b=min(J),max(J);c[i][a:b+1]=[d]*(b-a+1)
  for j in range(C):
   I=[i for i in range(R)if o[i][j]==d]
   if I:
    for i in range(min(I),max(I)+1):c[i][j]=d
 return[[L if i%3==2 or j%3==2 else c[i//3][j//3]for j in range(w)]for i in range(h)]
```