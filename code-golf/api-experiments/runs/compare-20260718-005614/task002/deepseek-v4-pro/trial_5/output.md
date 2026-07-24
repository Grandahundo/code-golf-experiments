```python
def p(g):
 h,w=len(g),len(g[0]);q={(i,j)for i in range(h)for j in range(w)if i%~-h*j%~-w<1&(g[i][j]==0)}
 while q:i,j=q.pop();g[i][j]==0and(g[i][j]:=2)and[q.add((x,y))for x,y in(i-1,j),(i+1,j),(i,j-1),(i,j+1)if(0<=x<h)&(0<=y<w)&(g[x][y]==0)]
 return[[{0:4,2:0}.get(v,v)for v in r]for r in g]
```