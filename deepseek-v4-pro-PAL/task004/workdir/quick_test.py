# Quick test of recursive function
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Copy the function from v_rec1
def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 R=lambda c,r,s:c<w and(r>=0 and(g[r][c]and(t:=s|(c>0<g[r][c-1]or c+1<w>g[r][c+1])and(r+1==h or any(g[r+1])<1),o[r].__setitem__(c+1-t,g[r][c]),R(c,r-1,t))[-1]or R(c,r-1,0))or R(c+1,h-1,0))
 R(0,h-1,0)
 return o

# Test on a simple case
g = [[0,0,0],[0,1,0],[0,0,0]]
print("Input:")
for r in g: print(r)
print("Output:")
o = p(g)
for r in o: print(r)
