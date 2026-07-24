```python
def p(g):r=[[c<<(c==1)for c in R]for R in g];h=len(r);P=next(p for p in range(1,h+1)if r[:p]*(h//p)+r[:h%p]==r);return[r[i%P]for i in range(h+h//2)]
```