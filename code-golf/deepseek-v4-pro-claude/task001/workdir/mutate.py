import sys, itertools
sys.path.insert(0,'.')
from gen import validate
D=validate()
cases=[(e['input'],e['output']) for s in('train','test') for e in D[s]]

def ok(src):
    ns={}
    try:
        exec(src,ns); p=ns['p']
        return all(p([list(r) for r in inp])==out for inp,out in cases)
    except Exception:
        return False

base="p=lambda g:[[x&y for x in a for y in b]for a in g for b in g]"
print("base",len(base),ok(base))
found=[]
# delete k chars
for k in (1,2,3):
    seen=set()
    for combo in itertools.combinations(range(len(base)),k):
        s=combo_set=set(combo)
        cand="".join(ch for i,ch in enumerate(base) if i not in combo_set)
        if cand in seen: continue
        seen.add(cand)
        if ok(cand):
            found.append((len(cand),cand))
    print("k=",k,"passing found so far:",len(found))
found=sorted(set(found))
for n,c in found[:20]:
    print(n,repr(c))
print("MIN:",found[0] if found else None)
