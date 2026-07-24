import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gen import validate
d=json.load(open('data.json'))['arc-gen']
v=validate();val=[e for s in('train','test')for e in v[s]]
ALL=[(e['input'],e['output'])for e in d]+[(e['input'],e['output'])for e in val]

def ok(src):
    ns={}
    try:exec(src,ns);p=ns['p']
    except Exception:return None
    try:
        for I,O in ALL:
            if p(I)!=O:return False
    except Exception:return False
    return True

cands=set()
gates=['any(b)','max(b)','sum(b)']
# arithmetic index, range form
for G in gates:
    cands.add(f'p=lambda g:[[a[c-(b[c-1]<{G})]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')
    cands.add(f'p=lambda g:[[a[c-({G}>b[c-1])]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')
# enumerate form giving x=a[c]
for G in gates:
    cands.add(f'p=lambda g:[[a[c-1]if b[c-1]<{G} else x for c,x in enumerate(a)]for a,b in zip(g,g[1:]+g)]')
# use enumerate on b to get u=b[c] shifted idea (out[c+1])... prefix
for G in gates:
    cands.add(f'p=lambda g:[[0]+[a[c-(b[c]<{G})]for c in range(len(a)-1)]for a,b in zip(g,g[1:]+g)]')
# variant: index b without wrap using [0]+b, arithmetic on padded a
for G in gates:
    cands.add(f'p=lambda g:[[([0]+a)[c+(u>={G})]for c,u in enumerate(b)]for a,b in zip(g,g[1:]+g)]')
# map-based
for G in gates:
    cands.add(f'p=lambda g:[[a[c-(b[c-1]<{G})]for c in range(len(b))]for a,b in zip(g,g[1:]+g)]')
# try b[c-1] via slice value with walrus? skip
res=[]
for s in cands:
    r=ok(s)
    if r:res.append((len(s),s))
res.sort()
print('PASSING (sorted):')
for L,s in res:print(L,s)
print('best:',res[0][0] if res else None)
