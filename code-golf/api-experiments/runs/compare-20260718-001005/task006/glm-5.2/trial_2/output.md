```python
def p(g):
 w=len(g[0])//2
 return[[2*(g[i][j]==1and g[i][j+w+1])for j in range(w)]for i in range(len(g))]
```