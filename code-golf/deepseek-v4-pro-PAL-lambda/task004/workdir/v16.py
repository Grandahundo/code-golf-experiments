p=lambda g:(
 w:=len(g[0]),g:=g+[[0]*w],o:=[[0]*w for _ in g[:-1]],r:=len(g)-1,
 [exec('while r:r-=1;x=g[r];y=g[r+1];[o[r].__setitem__(c+(v in y and(y[c]<1 or c+1<w and x[c+1]>0)),v)for c in range(w)if(v:=x[c])]')],
 o)[-1]
