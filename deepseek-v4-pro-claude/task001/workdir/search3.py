import sys
sys.path.insert(0,'.')
from gen import validate
D=validate()
cases=[(e['input'],e['output']) for s in('train','test') for e in D[s]]

def ok(src):
    ns={}
    try:
        exec(src,ns); p=ns['p']
        return all(p([list(r) for r in inp])==out for inp,out in cases)
    except Exception as ex:
        return "ERR:"+type(ex).__name__

C=[
 # reference
 "p=lambda g:[[x&y for x in a for y in b]for a in g for b in g]",
 # string-fractal then int-convert
 "p=lambda g:[[int(c)for c in d]for d in[''.join(x and r or'000'for x in a)for a in g for r in[''.join(map(str,b))for b in g]]]",
 # nested map with operator-free
 "p=lambda g:[[x&y for x in a for y in b]for a in g for b in g]",
 # broadcast/zip
 "p=lambda g:[[i&j for i,j in zip([v for v in a for _ in b],b*3)]for a in g for b in g]",
 # reduce over rows
 "from functools import reduce\np=lambda g:[[x&y for x in a for y in b]for a in g for b in g]",
 # sum of scaled blocks (list mult)
 "p=lambda g:[sum([b*(x>0)or[0]*3for x in a],[])for a in g for b in g]",
 # nested comprehension w/ single grid var reuse via product-free
 "p=lambda g:[[x&y for x in a for y in b]for b in g for a in g]",  # wrong (partial swap) - sanity
 # generator flatten + grouper
 "p=lambda g:[l[i:i+9]for l in[[x&y for a in g for b in g for x in a for y in b]]for i in range(0,81,9)]",
 # map(min,...) idea
 "p=lambda g:[[min(x,y)for x in a for y in b]for a in g for b in g]",
]
best=None
for c in C:
    r=ok(c); n=len(c)
    if r is True and (best is None or n<best[0]): best=(n,c)
    print(n, r, repr(c[:80]))
print("BEST:",best)
