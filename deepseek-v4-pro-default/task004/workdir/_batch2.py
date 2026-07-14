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
        try: g=p(inp)
        except Exception as ex: return ('ERR-run',repr(ex))
        if not np.array_equal(g,out): fails+=1
    return ('ok',fails)

cands = {
"base":"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
"bittilde":"p=lambda g:[[a[c-(b[~-c]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
"maxg":"p=lambda g:[[a[c-(b[c-1]<max(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
"revcmp":"p=lambda g:[[a[c-(any(b)>b[c-1])]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# swap zip order
"swapzip":"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for b,a in zip(g[1:]+g,g)]",
# use e as row-below var name irrelevant
# below via (g+g)[1:]
"gg":"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,(g+g)[1:])]",
# map form
"mapf":"p=lambda g:[[*map(lambda c:a[c-(b[c-1]<any(b))],range(len(a)))]for a,b in zip(g,g[1:]+g)]",
# walrus any once
"walrus":"p=lambda g:[[a[c-(b[c-1]<A)]for c in range(len(a))]for a,b in zip(g,g[1:]+g)if(A:=any(b))or 1]",
# use len via a in range with b
"lenb":"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(b))]for a,b in zip(g,g[1:]+g)]",
}
for k,s in cands.items():
    r=test(s); print(f"{len(s.encode()):3d} {r} {k}")
