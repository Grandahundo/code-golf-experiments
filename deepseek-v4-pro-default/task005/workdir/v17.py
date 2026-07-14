def p(g):
 E=0,1,2;D=-4,4,0;R=range(21)
 _,y,x=max((sum(x>0 for r in g[i:i+3]for x in r[j:j+3]),i,j)for i in R for j in R)
 o={(y+k*r+a,x+k*d+c):v for r in D for d in D if(v:=max(g[y+r+e][x+d+f]for e in E for f in E))for k in range(8)for a in E for c in E if g[y+a][x+c]}
 return[[o.get((i,j),0)for j in R]for i in R]
