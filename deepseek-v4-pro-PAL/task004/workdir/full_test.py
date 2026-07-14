import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gen import validate

# Copy the function from v_rec1
def p(g):
 h=len(g);w=len(g[0]);o=[[0]*w for _ in g]
 R=lambda c,r,s:c<w and(r>=0 and(g[r][c]and(t:=s|(c>0<g[r][c-1]or c+1<w>g[r][c+1])and(r+1==h or any(g[r+1])<1),o[r].__setitem__(c+1-t,g[r][c]),R(c,r-1,t))[-1]or R(c,r-1,0))or R(c+1,h-1,0))
 R(0,h-1,0)
 return o

data = validate()
all_ok = True
for split in ("train","test"):
    for i, ex in enumerate(data[split]):
        inp, exp = ex["input"], ex["output"]
        try:
            got = p(inp)
            ok = got == exp
            print(f"[{split} {i}] {'PASS' if ok else 'FAIL'}")
            if not ok:
                all_ok = False
                print(f"  Input {len(inp)}x{len(inp[0])}, Output {len(got)}x{len(got[0])}")
        except Exception as e:
            print(f"[{split} {i}] ERROR: {e}")
            all_ok = False
            import traceback
            traceback.print_exc()
print(f"\nAll passed: {all_ok}")
