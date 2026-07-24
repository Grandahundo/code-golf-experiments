import json
d = json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX = [(e['input'], e['output']) for e in (d['train'] + d['test'] + d['arc-gen'])]
def test(src):
    try:
        ns={}; exec(src, ns); p=ns['p']
    except Exception: return False
    for inp,out in EX:
        try:
            if p(inp)!=out: return False
        except Exception: return False
    return True
res=[]
def add(src):
    if test(src): res.append((len(src),src))

# Last-ditch 1-byte-saving scaffold ideas
cands = [
 # ~-c == c-1 (same len); -~c == c+1
 'p=lambda g:[[a[c-(b[~-c]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]',
 # merge: single comp won't nest; try using b for len (same)
 'p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(b))]for a,b in zip(g,g[1:]+g)]',
 # use *a to get length? no. try len(g[0])
 'p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(g[0]))]for a,b in zip(g,g[1:]+g)]',
 # can we drop parens using bitwise & (binds looser than -, so needs parens anyway)
 'p=lambda g:[[a[c-(any(b)>b[c-1])]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]',
 # enumerate variant reusing value nowhere
 'p=lambda g:[[a[i-(b[i-1]<any(b))]for i,_ in enumerate(a)]for a,b in zip(g,g[1:]+g)]',
 # try 'for*' no. try below as g[1:]+g[:1] shorter? no
 # try any(b) as `b>[0]*len(b)` no. try `[]<b` (compares list to empty) truthy iff b nonempty -> always True, wrong
 # try sum truthiness with 'and 1'
 'p=lambda g:[[a[c-(b[c-1]<max(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]',
]
for s in cands: add(s)
res.sort()
print("passing:")
for L,s in res: print(L, "<82!!" if L<82 else "", s)
