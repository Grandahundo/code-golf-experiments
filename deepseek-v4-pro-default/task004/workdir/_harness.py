import json, sys
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
        exec(src,ns)
        p=ns['p']
    except Exception as ex:
        return ('ERR-compile',str(ex))
    fails=0
    for inp,out in examples:
        try:
            g=p(inp)
        except Exception as ex:
            return ('ERR-run',str(ex))
        import numpy as np
        if not np.array_equal(g,out):
            fails+=1
    return ('ok',fails)
if __name__=='__main__':
    import sys
    src=sys.stdin.read()
    print(len(src.encode()), test(src))
