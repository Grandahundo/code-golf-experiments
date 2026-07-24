```python
def p(g):
 c=1
 def f(x,y):
  if 0<=x<len(g)and 0<=y<len(g[0])and g[x][y]==5:g[x][y]=c;f(x+1,y);f(x-1,y);f(x,y+1);f(x,y-1)
 for i,r in enumerate(g):
  for j,v in enumerate(r):
   if v==5:f(i,j);c+=1
 return g
```