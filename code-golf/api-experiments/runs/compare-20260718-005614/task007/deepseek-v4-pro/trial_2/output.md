```python
def p(g):
 d={(i+j)%3:v for i,r in enumerate(g)for j,v in enumerate(r)if v}
 return[[d[(i+j)%3]for j in range(len(r))]for i,r in enumerate(g)]
```