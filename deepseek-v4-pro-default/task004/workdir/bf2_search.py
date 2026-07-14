import json

d = json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX = [(e['input'], e['output']) for e in (d['train'] + d['test'] + d['arc-gen'])]

def test(src):
    try:
        ns = {}
        exec(src, ns)
        p = ns['p']
    except Exception:
        return False
    for inp, out in EX:
        try:
            if p(inp) != out:
                return False
        except Exception:
            return False
    return True

results = []
def add(src):
    if test(src):
        results.append((len(src), src))

# Explore alternate scaffolds and shifts.
# S = below-row expression list to try
BELOWS = ['g[1:]+g', 'g[1:]+g[:1]', '(g+g)[1:]']
GATES = ['any(b)', 'max(b)']

# Form 1: shift via slicing whole row, patch with b.  Row-level ternary.
# out row = [0]+a[:-1] shifted, but where any(b)==0 copy, and where b[c-1] keep a[c].
# Build with zip over (shifted, a, bshift)
for be in BELOWS:
    for G in GATES:
        # ternary with 'not u'
        add(f'p=lambda g:[[x,y][u<{G}]for x,y,u in zip([0]+a,a,[0]+b)]if 1 else 0 for a,b in zip(g,{be})]')

# Form 2: use walrus to cache gate per row inside inner (recomputed but named once? no gain) - skip

# Form 3: enumerate variants
for be in BELOWS:
    for G in GATES:
        add(f'p=lambda g:[[a[c-(b[c-1]<{G})]for c,_ in enumerate(a)]for a,b in zip(g,{be})]')

# Form 4: gate using b[c] instead of b[c-1] (data coincidence check)
for be in BELOWS:
    for G in GATES:
        add(f'p=lambda g:[[a[c-(b[c]<{G})]for c in range(len(a))]for a,b in zip(g,{be})]')
        add(f'p=lambda g:[[a[c-(b[c-1]<{G})]for c in range(len(a))]for a,b in zip(g,{be})]')

# Form 5: multiply-based: shift index = A*(b[c-1]==0) ; A=any(b)
for be in BELOWS:
    add(f'p=lambda g:[[a[c-any(b)*(0==b[c-1])]for c in range(len(a))]for a,b in zip(g,{be})]')
    add(f'p=lambda g:[[a[c-(any(b)and 0==b[c-1])]for c in range(len(a))]for a,b in zip(g,{be})]')

# Form 6: build shifted row [0]+a[:-1] and select via zip with mask from b
for be in BELOWS:
    for G in GATES:
        add(f'p=lambda g:[[y if u<{G} else x for x,y,u in zip(a,[0]+a,[0]+b)]for a,b in zip(g,{be})]')

# Form 7: gate as "b<[max?]" whole compare, or using count
for be in BELOWS:
    add(f'p=lambda g:[[a[c-(b[c-1]<sum(b))]for c in range(len(a))]for a,b in zip(g,{be})]')  # unsafe? test
    add(f'p=lambda g:[[a[c-(b[c-1]<len(b)and 1)]for c in range(len(a))]for a,b in zip(g,{be})]')

# Form 8: any(b) alternatives that are shorter
ALT_GATES = ['any(b)','max(b)','[]<b and 1']
for be in BELOWS:
    for G in ALT_GATES:
        add(f'p=lambda g:[[a[c-(b[c-1]<{G})]for c in range(len(a))]for a,b in zip(g,{be})]')

results.sort()
seen=set()
print("PASSING:")
for L,s in results:
    if s in seen:continue
    seen.add(s)
    print(L, s)
print("count", len(seen))
