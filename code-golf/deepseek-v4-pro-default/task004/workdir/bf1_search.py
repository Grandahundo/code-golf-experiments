import json, itertools, sys

d = json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
# All 265 examples: train(2)+test(1)+arc-gen(262)
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

# ---- Grammar pieces ----
BELOW = ['g[1:]+g']                       # row-below stream
GATE  = ['any(b)', 'max(b)']              # any-nonzero gate (both proven equivalent)

results = []  # (len, src)

def add(src):
    if test(src):
        results.append((len(src), src))

# Template A: range-index form.  out[c] = a[c - shift]
condA = [
    'b[c-1]<{G}',
    '{G}>b[c-1]',
]
for be in BELOW:
    for G in GATE:
        for cond in condA:
            c = cond.format(G=G)
            add(f'p=lambda g:[[a[c-({c})]for c in range(len(a))]for a,b in zip(g,{be})]')

# Template B: 3-stream select  [y,x][u<A]  (x=a[c-1],y=a[c],u=b[c-1])
selB = [
    '[y,x][u<{G}]',
    '[y,x][{G}>u]',
    '[x,y][u>={G}]',
    '[x,y][{G}<=u]',
]
for be in BELOW:
    for G in GATE:
        for sel in selB:
            s = sel.format(G=G)
            add(f'p=lambda g:[[{s}for x,y,u in zip([0]+a,a,[0]+b)]for a,b in zip(g,{be})]')

# Template C: col0=0 + 2-stream (y=a[c],z=a[c+1],v=b[c]) select for cols 1..W-1
selC = [
    '[y,z][v>={G}]',
    '[y,z][{G}<=v]',
    '[z,y][v<{G}]',
    '[z,y][{G}>v]',
]
for be in BELOW:
    for G in GATE:
        for sel in selC:
            s = sel.format(G=G)
            add(f'p=lambda g:[[0]+[{s}for y,z,v in zip(a,a[1:],b)]for a,b in zip(g,{be})]')

# Template D: arithmetic index forms
for be in BELOW:
    for G in GATE:
        add(f'p=lambda g:[[a[c-1]if b[c-1]<{G} else a[c]for c in range(len(a))]for a,b in zip(g,{be})]')
        add(f'p=lambda g:[[(a[c-1],a[c])[b[c-1]>={G}]for c in range(len(a))]for a,b in zip(g,{be})]')

results.sort()
print("PASSING CANDIDATES (sorted by length):")
seen=set()
for L, s in results:
    if s in seen: continue
    seen.add(s)
    print(L, s)
print("total passing:", len(seen))
