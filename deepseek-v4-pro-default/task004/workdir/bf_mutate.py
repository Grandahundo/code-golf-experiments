import json,itertools
d=json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX=[(e['input'],e['output']) for e in d['train']+d['test']+d['arc-gen']]

def test(src):
    ns={}
    try:
        exec(src,ns); p=ns['p']
        return all(p(i)==o for i,o in EX)
    except Exception:
        return False

base='p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]'
assert test(base), "base must pass"
found=set()

# single-char deletions
for i in range(len(base)):
    s=base[:i]+base[i+1:]
    if len(s)<82 and test(s): found.add(s)
# double-char deletions
for i in range(len(base)):
    for j in range(i+1,len(base)):
        s=base[:i]+base[i+1:j]+base[j+1:]
        if len(s)<82 and test(s): found.add(s)
# triple deletions (bounded)
for i,j,k in itertools.combinations(range(len(base)),3):
    s=base[:i]+base[i+1:j]+base[j+1:k]+base[k+1:]
    if len(s)<82 and test(s): found.add(s)

print('deletion-found:')
for s in sorted(found,key=len):
    print(len(s),repr(s))
if not found: print('none from deletions')
