import json

d = json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX = [(e['input'], e['output']) for e in (d['train'] + d['test'] + d['arc-gen'])]

def test(src):
    try:
        ns={}; exec(src, ns); p=ns['p']
    except Exception:
        return False
    for inp,out in EX:
        try:
            if p(inp)!=out: return False
        except Exception:
            return False
    return True

res=[]
def add(src):
    if test(src): res.append((len(src),src))

# OR / max based algebraic forms (single-color exploitation). A=any(b)
belows=['g[1:]+g']
for be in belows:
    # keep a[c] where b[c-1], else shifted a[c-1] when any(b) else a[c]
    add(f'p=lambda g:[[a[c]if b[c-1]or not any(b)else a[c-1]for c in range(len(a))]for a,b in zip(g,{be})]')
    add(f'p=lambda g:[[a[c-1]*(b[c-1]<any(b))or a[c]for c in range(len(a))]for a,b in zip(g,{be})]')
    add(f'p=lambda g:[[max(a[c-1]*(b[c-1]<any(b)),a[c]*(b[c-1]>0))for c in range(len(a))]for a,b in zip(g,{be})]')
    # bitwise or since single color
    add(f'p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,{be})]')  # baseline sanity

# gather: build index list then index a
for be in belows:
    add(f'p=lambda g:[[a[i]for i in[c-(b[c-1]<any(b))for c in range(len(a))]]for a,b in zip(g,{be})]')

# use map over range
for be in belows:
    add(f'p=lambda g:[[*map(a.__getitem__,[c-(b[c-1]<any(b))for c in range(len(a))])]for a,b in zip(g,{be})]')

res.sort()
print("PASSING:")
for L,s in res:
    print(L, s, "<82!" if L<82 else "")
print("count", len(res))
