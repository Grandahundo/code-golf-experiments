import json
d=json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX=[(e['input'],e['output']) for e in d['train']+d['test']+d['arc-gen']]
def test(src):
    ns={}
    try:
        exec(src,ns); p=ns['p']
        return all(p(i)==o for i,o in EX)
    except Exception:
        return False

gates=['any(b)','max(b)']
cands=set()

# Many inner-expression + iterator combos, all wrapped with outer zip(g,g[1:]+g)
OUT='p=lambda g:[[{INNER}]for a,b in zip(g,g[1:]+g)]'
inners=[]
for G in gates:
    # index forms
    inners+=[
        f'a[c-(b[c-1]<{G})]for c in range(len(a))',
        f'a[c-(b[c-1]<{G})]for c in range(len(b))',
        # enumerate binding value x=a[c]
        f'[x,a[c-1]][b[c-1]<{G}]for c,x in enumerate(a)',
        f'a[c-(b[c-1]<{G})]for c,_ in enumerate(a)',
        f'a[c-(u<{G})]for c,u in enumerate([0]+b[:-1])',
        # zip select forms
        f'[y,x][u<{G}]for x,y,u in zip([0]+a,a,[0]+b)',
        f'[0]+[[y,x][u<{G}]for x,y,u in zip(a,a[1:],b)][0:]'[:-4]+f'',  # placeholder
    ]
# clean placeholder junk
inners=[s for s in inners if 'placeholder' not in s and s.strip()]
for ie in inners:
    cands.add(OUT.replace('{INNER}',ie))

# forms that need [0]+ prefix at row level (out col0 always 0)
for G in gates:
    cands.add(f'p=lambda g:[[0]+[[y,x][u<{G}]for x,y,u in zip(a,a[1:],b)]for a,b in zip(g,g[1:]+g)]')
    cands.add(f'p=lambda g:[[0]+[a[c]if b[c-1]else a[c-1]for c in range(1,len(a))]for a,b in zip(g,g[1:]+g)]')  # ignores gate-blank; test

# map-based
for G in gates:
    cands.add(f'p=lambda g:[[a[c-(b[c-1]<{G})]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')

# try comparing with 0/1 shift via multiplication in index (no parens needed?)
for G in gates:
    cands.add(f'p=lambda g:[[a[c-(0<{G}>b[c-1])]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')

res=sorted((s for s in cands if test(s)),key=len)
print('PASS <=82 sorted:')
for s in res:
    mark=' <<<<< UNDER82' if len(s)<82 else ''
    print(len(s),repr(s),mark)
print('shortest',res[0] if res else None, len(res[0]) if res else None)
