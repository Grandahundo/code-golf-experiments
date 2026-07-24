import json
d=json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX=[(e['input'],e['output']) for e in d['train']+d['test']+d['arc-gen']]
def test(src):
    ns={}
    try:
        exec(src,ns); p=ns['p']
        return all(p(i)==o for i,o in EX)
    except Exception:
        return False

# The shift boolean at column c decides out[c]=a[c-1] (shift) vs a[c] (keep).
# Replace GATE in: a[c-(GATE)] . GATE must be 0/1 (True/False ok).
# Try LOCAL gates (no any/max scan) using neighbors of b and a.
gate_exprs = [
 'b[c-1]<b[c]',
 'b[c]>b[c-1]',
 'b[c-1]<a[c]',      # mixes a
 'b[c-1]<b[c-2]',
 'b[c]and b[c-1]<1',
 'b[c]>b[c-1]<1',    # nonsense but test
 'b[c-1]<b[c]or b[c-1]<b[c-2]',
 'b[c]*(b[c-1]<1)',
 'b[c-1]<max(b[c-1:c+1])',
 '0<b[c]>b[c-1]',
 'b[c-1]<b[c]==b[c]', # test
 'b[c-1]<(b[c]or b[c-2])',
 'b[c]>b[c-1]==0',
]
cands=set()
for g in gate_exprs:
    cands.add(f'p=lambda g:[[a[c-({g})]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')

# also non-parenthesised single ops (if precedence allows a[c-EXPR])
res=[]
for s in cands:
    ok=test(s)
    res.append((ok,len(s),s))
res.sort()
print('results (ok,len,src):')
for ok,l,s in sorted(res,key=lambda t:(not t[0],t[1])):
    print(ok,l,repr(s))
passing=[ (l,s) for ok,l,s in res if ok]
print('\nPASSING under 82:',[ (l,s) for l,s in passing if l<82])
