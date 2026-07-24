import json,itertools
d=json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX=[(e['input'],e['output']) for e in d['train']+d['test']+d['arc-gen']]

def test_full(src):
    try:
        ns={};exec('p='+src,ns);p=ns['p']
        return all(p(i)==o for i,o in EX)
    except Exception:
        return False

# The fixed scaffold, EXPR is the inner cell value using vars a,b,c
SCAF='lambda g:[[%s for c in range(len(a))]for a,b in zip(g,g[1:]+g)]'
# but note real best removes space before 'for'; emulate by not adding space:
SCAF='lambda g:[[%sfor c in range(len(a))]for a,b in zip(g,g[1:]+g)]'

# Grammar BFS for EXPR (must end without trailing space; keep <=19 chars)
# atoms
atoms=['a[c]','a[c-1]','a[~-c]','a[-~c]','a[c+1]','b[c]','b[c-1]','b[~-c]',
       'any(b)','max(b)','c','0','1']
# We build a[INDEX] forms and select forms.
idx_terms=['c','c-1','c+1','~-c','-~c',
           'c-(b[c-1]<any(b))','c-(b[~-c]<any(b))','c-(b[c-1]<max(b))',
           'c-(any(b)>b[c-1])','c-b[c-1]//9','c-(b[c-1]<1)*any(b)']
cands=set()
for it in idx_terms:
    e='a[%s]'%it
    if len(e)<=19: cands.add(SCAF%e)

# select forms [X,Y][cond]
Xs=['a[c]','a[~-c]','a[c-1]']
conds=['b[c-1]<any(b)','b[~-c]<any(b)','b[c-1]<max(b)','any(b)>b[c-1]']
for X in Xs:
  for Y in Xs:
    if X==Y:continue
    for cd in conds:
      e='[%s,%s][%s]'%(X,Y,cd)
      if len(e)<=19: cands.add(SCAF%e)

# arithmetic forms
for cd in conds:
  for e in ['a[c]*(%s)'%cd,'a[c-(%s)]'%cd]:
    if len(e)<=19: cands.add(SCAF%e)

# Alternative scaffolds that might be shorter than 62 fixed bytes
alt=[
 # rely on last row blank: iterate zip(g,g[1:]) then append? -> need all rows; try g[1:]+g[:1]
 'lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]',
 # transpose attempt (likely wrong) - just to see
 # use map?
 # width via len(g[0]) - longer, skip
]
for s in alt: cands.add(s)

good=sorted((len(s)+2,s) for s in cands if test_full(s))
print('PASSING (bytes incl p=, src):')
for l,s in good: print(l,s)
print('UNDER 82:',[x for x in good if x[0]<82])
print('tested',len(cands))
