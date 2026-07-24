```python
def p(g):
 s=[0]*3
 for i,r in enumerate(g):
  for j,v in enumerate(r):
   if v:s[(i+j)%3]=v
 return[[s[(i+j)%3]for j in range(len(r))]for i,r in enumerate(g)]
```