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
    try: exec(src,ns); p=ns['p']
    except Exception as ex: return ('ERR-compile',repr(ex))
    fails=0
    for inp,out in examples:
        try: g=p(inp)
        except Exception as ex: return ('ERR-run',repr(ex))
        if not np.array_equal(g,out): fails+=1
    return ('ok',fails)
cands = {
# reduce over? no. try single-shift-index w/ slice a[c-1:c+1]
"slice":"p=lambda g:[[a[c-1:c+1][b[c-1]>=any(b)]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# try building shifted row s and blend via zip
"blend":"p=lambda g:[[[y,x][u<any(b)]for x,y,u in zip([0]+a,a,[0]+b)]for a,b in zip(g,g[1:]+g)]",
# any(b) via *b test? no. try sum gate (expect fails)
"sumg":"p=lambda g:[[a[c-(b[c-1]<sum(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# use bool from 'any(b)and not b[c-1]'
"andnot":"p=lambda g:[[a[c-(any(b)>b[c-1])]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# nest any into b via list mult -- longer, sanity
# hardcode nothing
# try: a[c-(0<b[::-1]... ) no
}
for k,s in cands.items():
    r=test(s); print(f"{len(s.encode()):3d} {r} {k}")
