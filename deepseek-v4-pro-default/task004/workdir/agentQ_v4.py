import json
d=json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX=[(e['input'],e['output']) for e in d['train']+d['test']+d['arc-gen']]

# data facts
print('last row all blank:', all(not any(i[-1]) for i,o in EX))
print('row0 blank:', all(not any(i[0]) for i,o in EX))

def test_full(src):
    try:
        ns={};exec('p='+src,ns);p=ns['p']
        return all(p(i)==o for i,o in EX)
    except Exception:
        return False

cands=set()

# Scaffold S1: for c in range(len(a)); vars a,b,c
S1='lambda g:[[%sfor c in range(len(a))]for a,b in zip(g,%s)]'
belows=['g[1:]+g','(g+g)[1:]','g[1:]+g[:1]']
inner1=['a[c-(b[c-1]<any(b))]','a[c-(b[~-c]<any(b))]','a[c-(b[c-1]<max(b))]',
        'a[c-(any(b)>b[c-1])]','a[c-(any(b)>b[~-c])]']
for B in belows:
  for e in inner1:
    cands.add(S1%(e,B))

# Scaffold S1b: last row blank -> zip(g,g[1:]) + append last row
S1b='lambda g:[[%sfor c in range(len(a))]for a,b in zip(g,g[1:])]+g[-1:]'
for e in inner1:
  cands.add(S1b%e)

# Scaffold S2: enumerate giving x=a[c]
S2='lambda g:[[%sfor c,x in enumerate(a)]for a,b in zip(g,g[1:]+g)]'
inner2=['a[c-(b[c-1]<any(b))]','[a[~-c],x][b[c-1]>=any(b)]','[x,a[~-c]][b[c-1]<any(b)]',
        'x if b[c-1]else a[~-c]']  # note last is wrong when not any(b); will fail-filter
for e in inner2:
  cands.add(S2%e)

# Scaffold S3: zip triple y=a[c],x=a[c-1],u=b[c-1]
S3='lambda g:[[%sfor y,x,u in zip(a,[0]+a,[0]+b)]for a,b in zip(g,g[1:]+g)]'
inner3=['[y,x][u<any(b)]','x if u<any(b)else y','[y,x][u<max(b)]']
for e in inner3:
  cands.add(S3%e)

# Scaffold S4: shift b by a column so gate uses b[c] (4 chars) -- build shifted below
S4='lambda g:[[a[c-(b[c]<any(b))]for c in range(len(a))]for a,b in zip(g,[[0]+r for r in g[1:]+g])]'
cands.add(S4)

# Scaffold S5: def form (unlikely shorter) - skip

good=sorted((len(s)+2,s) for s in cands if test_full(s))
print('\nPASSING (bytes incl p=, src):')
for l,s in good: print(l,s)
u=[x for x in good if x[0]<82]
print('\nUNDER 82:',u)
print('tested',len(cands))
