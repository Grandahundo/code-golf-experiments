```python
def p(g):
 m,n=len(g),len(g[0])
 def f(x,y):
  if(m>x>=0)&(n>y>=0)&(g[x][y]<1):g[x][y]=2;f(x-1,y);f(x+1,y);f(x,y-1);f(x,y+1)
 for i in range(m):f(i,0);f(i,n-1)
 for j in range(n):f(0,j);f(m-1,j)
 return[[(4,0,0,3)[v]for v in r]for r in g]
```