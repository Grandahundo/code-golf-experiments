```python
p=lambda g:[[(r[c]&r[s+1+c])*2for c in range(s:=len(r)//2)]for r in g]
```