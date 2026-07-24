import json, itertools

d = json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX = [(e['input'], e['output']) for e in (d['train'] + d['test'] + d['arc-gen'])]

def test(src):
    try:
        ns = {}; exec(src, ns); p = ns['p']
    except Exception:
        return False
    for inp, out in EX:
        try:
            if p(inp) != out: return False
        except Exception:
            return False
    return True

results=[]
def add(src):
    if len(src)<82 and test(src):
        results.append((len(src),src))

# Enumerate index-arithmetic inner families with many gate spellings and index forms.
gates = ['any(b)','max(b)']
# shift condition spellings (value is 0/1, True when we should use a[c-1])
conds = ['b[c-1]<{G}','{G}>b[c-1]']
# iteration spellings giving index c
iters = ['for c in range(len(a))','for c,_ in enumerate(a)','for c,_ in enumerate(b)']
belows = ['g[1:]+g']

for be in belows:
    for G in gates:
        for cond in conds:
            cc=cond.format(G=G)
            for it in iters:
                add(f'p=lambda g:[[a[c-({cc})]{it}]for a,b in zip(g,{be})]')

# Try dropping outer paren via multiplication precedence variants (may be longer, but check)
for be in belows:
    for G in gates:
        add(f'p=lambda g:[[a[c-({G}>b[c-1])]for c in range(len(a))]for a,b in zip(g,{be})]')

# Try b[c-1] gate combined with a-based any (data coincidence: any(a) instead of any(b)?)
for be in belows:
    add(f'p=lambda g:[[a[c-(b[c-1]<any(a))]for c in range(len(a))]for a,b in zip(g,{be})]')
    add(f'p=lambda g:[[a[c-(b[c-1]<max(a))]for c in range(len(a))]for a,b in zip(g,{be})]')

# Whole-row: maybe using sum with threshold, or 'b>[]'
for be in belows:
    for G in ['sum(b)and 1','bool(sum(b))','1>0<max(b)']:
        add(f'p=lambda g:[[a[c-(b[c-1]<{G})]for c in range(len(a))]for a,b in zip(g,{be})]')

results.sort()
print("UNDER-82 PASSING:", len(results))
for L,s in results:
    print(L,s)
if not results:
    print("none under 82 in this family")
