def p(g,i=0,o=0):
 if 0==o:w=len(g[0]);o[:]=[[0]*w for _ in g]
 if i>=len(g)*len(g[0]):return o
 r=i//len(g[0]);c=i%len(g[0]);v=g[r][c]
 if v:a=r and v in g[r-1];b=r<len(g)-1 and v in g[r+1];o[r][c+(a<1 or b and g[r+1][c]!=v)]=v
 return p(g,i+1,o)
