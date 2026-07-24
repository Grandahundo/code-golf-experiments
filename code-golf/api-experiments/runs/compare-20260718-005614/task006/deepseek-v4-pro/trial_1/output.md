```python
p=lambda g:[[2*(r[i]*r[(c:=len(r)//2)+1+i]==1)for i in range(c)]for r in g]
```