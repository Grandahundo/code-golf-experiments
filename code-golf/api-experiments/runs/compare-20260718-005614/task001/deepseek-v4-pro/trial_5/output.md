```python
def p(g):n=len(g);return[[g[i%n][j%n]*(g[i//n][j//n]>0)for j in range(n*n)]for i in range(n*n)]
```