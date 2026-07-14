import json,itertools
d=json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX=[(e['input'],e['output']) for e in d['train']+d['test']+d['arc-gen']]
def T(src):
    try:
        ns={};exec('p='+src,ns);p=ns['p']
        return all(p(i)==o for i,o in EX)
    except Exception: return False

cands=set()
# c-1 spellings
cm1=['c-1','~-c']
# row-nonblank detectors (must equal any(b) semantics on this data)
NB=['any(b)','max(b)','sum(b)and 9','max(map(abs,b))']
# gate producing 1 when (below nonblank and b[c-1]==0)
for x in cm1:
  for nb in NB:
    for g in ['b[%s]<%s'%(x,nb),'%s>b[%s]'%(nb,x)]:
      cands.add('lambda g:[[a[c-(%s)]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]'%g)
# multiply form a[c-nb*(b<1)]
for x in cm1:
  for nb in NB:
    cands.add('lambda g:[[a[c-%s*(b[%s]<1)]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]'%(nb,x))
# below variants
for below in ['g[1:]+g','(g+g)[1:]','g[1:]*2','g[1:]+g[:1]','g[1:]+[g[0]]','g[1:]+g[-1:]']:
  cands.add('lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,%s)]'%below)
# use x=a[c] via enumerate, arithmetic select (values single color)
for g in ['b[c-1]<any(b)','b[~-c]<any(b)']:
  cands.add('lambda g:[[a[c-(%s)]for c,x in enumerate(a)]for a,b in zip(g,g[1:]+g)]'%g)
# whole-grid max as nonblank? (wrong generally, test anyway)
cands.add('lambda g:[[a[c-(b[c-1]<max(max(g)))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')
# shift b by column to use b[c] (needs prebuilt) - measure
cands.add('lambda g:[[a[c-(u<any(b))]for c,u in enumerate([0]+b)][:len(a)]for a,b in zip(g,g[1:]+g)]')

res=sorted((len(s)+2,s) for s in cands if T(s))
print('min passing len:', res[0][0] if res else None)
for l,s in res[:15]: print(l,s)
under=[x for x in res if x[0]<82]
print('UNDER 82:', under)
print('tested',len(cands),'passing',len(res))
