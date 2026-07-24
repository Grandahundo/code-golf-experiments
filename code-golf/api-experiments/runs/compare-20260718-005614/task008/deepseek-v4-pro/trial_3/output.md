```python
def p(g):
 E=enumerate;s={(i,j)for i,r in E(g)for j,v in E(r)if v==8};t={(i,j)for i,r in E(g)for j,v in E(r)if v==2}
 a,b=map(min,zip(*s));c,d=map(max,zip(*s));e,f=map(min,zip(*t));g,h=map(max,zip(*t))
 dr=(g<a)*(a-1-g)+(e>c)*(c+1-e);dc=(h<b)*(b-1-h)+(f>d)*(d+1-f)
 o=[[8*(v==8)for v in r]for r in g]
 for i,j in t:o[i+dr][j+dc]=2
 return o
```