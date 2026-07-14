def p(g):
 G=range;r=G(3);R=-1,0,1
 y,x=max((sum(g[i+a][j+b]>0for a in r for b in r),i,j)for i in G(19)for j in G(19))[1:]
 D={(y+4*k*u+a,x+4*k*v+b):w for u in R for v in R if(w:=max(g[y+4*u+a][x+4*v+b]for a in r for b in r))for k in G(u*u|v*v,8)for a in r for b in r if g[y+a][x+b]}
 return[[D.get((i,j),0)for j in G(21)]for i in G(21)]
