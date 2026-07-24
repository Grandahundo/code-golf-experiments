```python
p=lambda g:[[2*(r[j]&r[j+len(r)//2+1])for j in range(len(r)//2)]for r in g]
```