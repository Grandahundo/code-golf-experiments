```python
def p(g):
    R=len(g);C=len(g[0])
    rr=[];rc=[];ar=[];ac=[]
    for i in range(R):
        for j in range(C):
            v=g[i][j]
            if v==2:rr+=[i];rc+=[j]
            elif v==8:ar+=[i];ac+=[j]
    rR0,rR1,rC0,rC1=min(rr),max(rr),min(rc),max(rc)
    aR0,aR1,aC0,aC1=min(ar),max(ar),min(ac),max(ac)
    dr=dc=0
    ho=rC1>=aC0 and rC0<=aC1
    vo=rR1>=aR0 and rR0<=aR1
    if rR1<aR0 and ho:dr=aR0-rR1-1
    if rR0>aR1 and ho:dr=aR1-rR0+1
    if rC1<aC0 and vo:dc=aC0-rC1-1
    if rC0>aC1 and vo:dc=aC1-rC0+1
    o=[[0]*C for _ in range(R)]
    for i in range(R):
        for j in range(C):
            if g[i][j]==2:o[i+dr][j+dc]=2
            elif g[i][j]==8:o[i][j]=8
    return o
```