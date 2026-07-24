```python
def p(g):
 c=[0]*3
 for i,r in enumerate(g):
  for j,v in enumerate(r):
   if v:c[(i+j)%3]=v
 return[[c[(i+j)%3]for j in range(len(r))]for i,r in enumerate(g)]
```