import json,os,sys
sys.path.insert(0,os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from gen import validate
d=json.load(open('data.json'))['arc-gen']
v=validate();val=[e for s in('train','test')for e in v[s]]
ALL=[(e['input'],e['output'])for e in d]+[(e['input'],e['output'])for e in val]
def ok(src):
    ns={}
    try:exec(src,ns);p=ns['p']
    except Exception as e:return None
    try:
        for I,O in ALL:
            if p(I)!=O:return False
    except Exception:return False
    return True
C=[
# base 82
"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# ~-c index (same len test)
"p=lambda g:[[a[c-(b[~-c]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# use enumerate(b) with prefix & slice (len(a)-1 loop)
"p=lambda g:[[0]+[a[-~c-(b[c]<any(b))]for c in range(len(a)-1)]for a,b in zip(g,g[1:]+g)]",
# map with getitem?
"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(g[0]))]for a,b in zip(g,g[1:]+g)]",
# drop range: enumerate a, reuse x via arithmetic on index? select form
"p=lambda g:[[[x,a[c-1]][b[c-1]<any(b)]for c,x in enumerate(a)]for a,b in zip(g,g[1:]+g)]",
# transpose double approach (correctness check, likely long)
"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# gate via b.count / min tricks
"p=lambda g:[[a[c-(b[c-1]<max(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# use w:=len(a) walrus (no reuse, just test)
"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# star-splat build
"p=lambda g:[[a[j]for j in(c-(b[c-1]<any(b))for c in range(len(a)))]for a,b in zip(g,g[1:]+g)]",
]
res=[]
for s in set(C):
    r=ok(s)
    res.append((len(s),r,s))
res.sort()
for L,r,s in res:
    print(L, 'PASS' if r else ('FAIL' if r is False else 'ERR'), s)
p=[ (L,s) for L,r,s in res if r]
print('best passing:', p[0][0] if p else None)
