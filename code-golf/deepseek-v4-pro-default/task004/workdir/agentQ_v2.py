import json,itertools
d=json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX=[(e['input'],e['output']) for e in d['train']+d['test']+d['arc-gen']]

def test(src):
    try:
        ns={};exec('p='+src,ns);p=ns['p']
        return all(p(i)==o for i,o in EX)
    except Exception:
        return False

# Enumerate gate expressions G (a boolean 0/1 shift) from atoms/ops.
# We want the FULL lambda strictly < 82 bytes.
# Scaffold A: a[c-(G)] with for c in range(len(a))
SA='lambda g:[[a[c-(%s)]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]'
# atoms referencing below-left and row-below nonblankness
belowleft=['b[c-1]','b[~-c]']  # b[~-c]==b[c-1]
rownon=['any(b)','max(b)']
ops=['<','>','<=','>=','!=','==']
Gs=set()
for bl in belowleft:
  for rn in rownon:
    Gs.add('%s<%s'%(bl,rn))
    Gs.add('%s>%s'%(rn,bl))
    Gs.add('%s>%s'%(bl,rn))  # wrong dir, will fail, filtered
    Gs.add('%s and %s<1'%(rn,bl))
    Gs.add('%s>%s<1'%(rn,bl))
# also try replacing any(b) with tricks
for bl in belowleft:
  Gs.add('%s<max(b)'%bl)
  Gs.add('%s<sum(b)'%bl)

cands=set()
for G in Gs:
    cands.add(SA%G)

# Scaffold B: a[c-any(b)*...] arithmetic shift variants
for bl in belowleft:
  for rn in rownon:
    cands.add('lambda g:[[a[c-%s*(%s<1)]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]'%(rn,bl))

# Scaffold C: use ~-c for c-1 in the index too: a[~-c] == a[c-1]. Maybe shift differently.
# out[c]=a[c] if (b[c-1] or not any(b)) else a[c-1]; select via [a[c-1],a[c]][cond]
for bl in belowleft:
  for rn in rownon:
    cands.add('lambda g:[[[a[~-c],a[c]][%s>0 or %s<1]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]'%(bl,rn))

good=sorted((len(s)+2,s) for s in cands if test(s))
print('PASSING (byte-count-with-p=, src):')
for l,s in good:
    print(l,s)
print('under82:',[ (l,s) for l,s in good if l<82])
print('tested',len(cands))
