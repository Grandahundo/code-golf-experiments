```python
def p(g):P=1;while g[:-P]!=g[P:]:P+=1;return[[x*2 for x in g[i%P]]for i in range(9)]
```