from common import*
def p(g):
 R,C=max(all_pixels(19,19),key=lambda x:sum(g[x[0]+i][x[1]+j]>0for i,j in all_pixels(3,3)))
 o=grid(21,21)
 for r,c in all_pixels(21,21):
  if v:=g[r][c]:
   d=(r-R)//4;e=(c-C)//4;a=R+d*4;b=C+e*4
   while-4<a<25and-4<b<25:
    for i,j in all_pixels(3,3):
     if g[R+i][C+j]:draw(o,a+i,b+j,v)
    if d==e==0:break
    a+=d*4;b+=e*4
 return o
