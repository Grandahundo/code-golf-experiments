import json
import numpy as np
from gen import validate
d=json.load(open('data.json'))
V=validate()
examples=[(e['input'],e['output']) for e in d['arc-gen']]
for s in ('train','test'):
    for e in V[s]:
        examples.append((e['input'],e['output']))

def test(src):
    ns={}
    try:
        exec(src,ns); p=ns['p']
    except Exception as ex:
        return ('ERR-compile',repr(ex))
    fails=0
    for inp,out in examples:
        try:
            g=p(inp)
        except Exception as ex:
            return ('ERR-run',repr(ex))
        if not np.array_equal(g,out):
            fails+=1
    return ('ok',fails)

cands = {
"baseline82":"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# select new-align
"selnew":"p=lambda g:[[0]+[[y,x][u<any(b)]for x,y,u in zip(a,a[1:],b)]for a,b in zip(g,g[1:]+g)]",
# index new-align
"idxnew":"p=lambda g:[[0]+[a[c+(any(b)<=b[c])]for c in range(len(a)-1)]for a,b in zip(g,g[1:]+g)]",
# enumerate reuse y
"enum":"p=lambda g:[[[y,a[c-1]][b[c-1]<any(b)]for c,y in enumerate(a)]for a,b in zip(g,g[1:]+g)]",
# max gate
"maxgate":"p=lambda g:[[a[c-(b[c-1]<max(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# use *g unpack? no
# zip a with shifted using [0]+b only, index c via range
"idxb":"p=lambda g:[[a[c-(v<any(b))]for c,v in enumerate([0]+b)][:len(a)]for a,b in zip(g,g[1:]+g)]",
}
for k,s in cands.items():
    r=test(s)
    print(f"{len(s.encode()):3d} {r} {k}")
