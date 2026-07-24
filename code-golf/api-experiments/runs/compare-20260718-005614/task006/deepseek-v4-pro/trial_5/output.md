```python
p=lambda g:[[2*a*b for a,b in zip(r[:(c:=len(r)//2)],r[c+1:])]for r in g]
```