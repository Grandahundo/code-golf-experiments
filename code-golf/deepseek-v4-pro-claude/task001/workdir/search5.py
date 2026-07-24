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
    except Exception as e:
        return "ERR:"+type(e).__name__
C=[
 "p=lambda g:[[x&y for x in a for y in b]for a in g for b in g]",                       # 61 ref
 # flat + reshape via slicing
 "p=lambda g:(f:=[x&y for a in g for b in g for x in a for y in b]) and[f[i:i+9]for i in range(0,81,9)]",
 # string build + int convert
 "p=lambda g:[[int(v)for v in ''.join(b if x else'000'for x in a)]for a in[*map(''.join,[[*map(str,r)]for r in g])]for b in[*map(''.join,[[*map(str,r)]for r in g])]]",
 # broadcast-zip inner
 "p=lambda g:[[x&y for x,y in zip([v for v in a for _ in a],b*3)]for a in g for b in g]",
 # map over product-free
 "p=lambda g:[sum([[x&y for y in b]for x in a],[])for a in g for b in g]",
 # nested with * flatten attempt (chain)
 "from itertools import chain\np=lambda g:[[*chain(*[[x&y for y in b]for x in a])]for a in g for b in g]",
 # reduce concat of bands
 "p=lambda g:sum([[[x&y for x in a for y in b]for b in g]for a in g],[])",
]
r=[]
for c in C:
    v=ok(c)
    print(len(c), v, repr(c[:75]))
    if v is True: r.append((len(c),c))
print("MIN PASS:", min(r) if r else None)
