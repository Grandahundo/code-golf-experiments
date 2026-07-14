import json
d=json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX=[(e['input'],e['output']) for e in d['train']+d['test']+d['arc-gen']]

def test(src):
    ns={}
    try:
        exec(src,ns)
        p=ns['p']
        for i,o in EX:
            if p(i)!=o: return False
        return True
    except Exception:
        return False

cands=set()

# gate expressions equivalent to any(b) (0/1 nonblank indicator)
gates=['any(b)','max(b)']
# comparison forms for shift bool at column c: True iff row-below nonblank AND b[c-1]==0
def cmps(gate):
    return [
        f'b[c-1]<{gate}',
        f'{gate}>b[c-1]',
    ]
# element (index form) using c
def elems_index(cmp):
    return [
        f'a[c-({cmp})]',
    ]
# pairings
pairs=['zip(g,g[1:]+g)']

# ---- INDEX FORM family ----
for gate in gates:
    for cmp in cmps(gate):
        for el in elems_index(cmp):
            for pr in pairs:
                cands.add(f'p=lambda g:[[{el}for c in range(len(a))]for a,b in {pr}]')
                # len(b) instead of len(a)
                cands.add(f'p=lambda g:[[{el}for c in range(len(b))]for a,b in {pr}]')

# ---- SELECT FORM family ----
for gate in gates:
    cands.add(f'p=lambda g:[[[y,x][u<{gate}]for x,y,u in zip([0]+a,a,[0]+b)]for a,b in zip(g,g[1:]+g)]')
    # a[1:] variant with [0]+ prefix
    cands.add(f'p=lambda g:[[0]+[[y,x][u<{gate}]for x,y,u in zip(a,a[1:],b)]for a,b in zip(g,g[1:]+g)]')

# ---- shift-by-one index form ----
for gate in gates:
    cands.add(f'p=lambda g:[[0]+[a[j+(b[j]>={gate})]for j in range(len(a)-1)]for a,b in zip(g,g[1:]+g)]')

# ---- b[c] variants (test if geometrically equivalent) ----
for gate in gates:
    cands.add(f'p=lambda g:[[a[c-(b[c]<{gate})]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')
    cands.add(f'p=lambda g:[[a[c-(b[c-1]<{gate})]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')

# ---- short-circuit + empty-tail pairing ----
for gate in gates:
    cands.add(f'p=lambda g:[[a[c-({gate}and b[c-1]<1)]for c in range(len(a))]for a,b in zip(g,g[1:]+[[]])]')
    cands.add(f'p=lambda g:[[a[c-({gate}and b[c-1]<1)]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')

# ---- prepend-zero-column preprocessing ideas via nested walrus ----
# h=[[0]+r for r in g]; process then strip col0. Try def form.
cands.add('''def p(g):
 h=[[0]+r for r in g]
 return [[a[c-(b[c-1]<any(b))]for c in range(len(a))][1:]for a,b in zip(h,h[1:]+h)]''')

# ---- tuple-index element ----
for gate in gates:
    cands.add(f'p=lambda g:[[(a[c],a[c-1])[b[c-1]<{gate}]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')

res=[]
for s in cands:
    if test(s):
        res.append(s)
res.sort(key=len)
print('PASSING candidates:')
for s in res:
    print(len(s), repr(s))
if res:
    print('\nSHORTEST:',len(res[0]))
