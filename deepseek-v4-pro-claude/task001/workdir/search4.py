import sys, itertools
sys.path.insert(0,'.')
from gen import validate
D=validate()
cases=[(e['input'],e['output']) for s in('train','test') for e in D[s]]

def ok(src):
    ns={}
    try:
        exec(src,ns); p=ns['p']
        return all(p([list(r) for r in inp])==out for inp,out in cases)
    except Exception:
        return False

cands=set()
ops=["x&y","y&x","x*y","x|y","x^y","min(x,y)","x*(y>0)","y*(x>0)","x and y","y and x"]
# 4-loop nested: [[OP for INNER1 for INNER2]for OUTER1 for OUTER2]
il=["for x in a for y in b","for y in b for x in a","for x in a for y in c","for y in c for x in b"]
ol=["for a in g for b in g","for b in g for a in g","for a in g for c in g","for b in g for c in g"]
for op in ops:
    for i in il:
        for o in ol:
            cands.add(f"p=lambda g:[[{op} {i}]{o}]")
# index forms with default range
for op in ["g[i//3][j//3]&g[i%3][j%3]","g[i%3][j%3]&g[i//3][j//3]"]:
    cands.add(f"p=lambda g,R=range(9):[[{op}for j in R]for i in R]")
# tile-mask/zip forms
cands.add("p=lambda g:[[x&y for x,y in zip(r*3,[v for v in a for _ in a])]for a in g for r in g]")
cands.add("p=lambda g:[[x&y for x in a for y in b]for a in g for b in g]")

res=[]
for c in cands:
    if ok(c): res.append((len(c),c))
res.sort()
print("total tested:",len(cands),"passing:",len(res))
for n,c in res[:15]:
    print(n,repr(c))
