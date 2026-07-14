import json,itertools
d=json.load(open('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004/data.json'))
EX=[(e['input'],e['output']) for e in d['train']+d['test']+d['arc-gen']]

def test(src):
    try:
        ns={}
        exec('p='+src,ns)
        p=ns['p']
        for inp,out in EX:
            if p(inp)!=out: return False
        return True
    except Exception:
        return False

# Building blocks
# BELOW expressions (used as second arg of zip(g,BELOW))
belows=['g[1:]+g','g[1:]+g[:1]','(g+g)[1:]','g[1:]+[g[0]]','g[-1:]+g','g[1:]+g[-1:]']
# GATE expressions -> boolean shift (variables a,b,c)
gates=['b[c-1]<any(b)','b[c-1]<max(b)','any(b)>b[c-1]','max(b)>b[c-1]',
       'b[c-1]<sum(b)','not b[c-1]<any(b)','b[c-1]<any(b)and 1',
       'b[c-1]==0<any(b)','any(b)and b[c-1]<1','b[c-1]<any(b)']
# INNER templates using gate G -> cell value
inner_tpls=['a[c-(%s)]','a[c-1]if %s else a[c]','[a[c],a[c-1]][%s]',
            '(a[c],a[c-1])[%s]']

cands=set()
for G in gates:
    for tpl in inner_tpls:
        try: inner=tpl%G
        except: continue
        for B in belows:
            src='lambda g:[[%s for c in range(len(a))]for a,b in zip(g,%s)]'%(inner,B)
            cands.add(src)

# Also enumerate-based structure: for c,x in enumerate(a) gives x=a[c]
for G in ['b[c-1]<any(b)','b[c-1]<max(b)']:
    for inner in ['a[c-(%s)]'%G,'[x,a[c-1]][%s]'%G]:
        for B in belows:
            src='lambda g:[[%s for c,x in enumerate(a)]for a,b in zip(g,%s)]'%(inner,B)
            cands.add(src)

# zip-triple structure: y=a[c], x=a[c-1], u=b[c-1]
for A in ['any(b)','max(b)']:
    for sel in ['[y,x][u<%s]'%A,'x if u<%s else y'%A,'y if u<%s else x'%A]:
        for pre in ['zip(a,[0]+a,[0]+b)','zip(a,a[-1:]+a,b[-1:]+b)']:
            src='lambda g:[[%s for y,x,u in %s]for a,b in zip(g,%s)]'%(sel,pre,'g[1:]+g')
            cands.add(src)

good=[(len(s),s) for s in cands if test(s)]
good.sort()
print('PASSING candidates (len, src):')
for l,s in good:
    print(l+2,s)  # +2 for 'p='
print('total tested',len(cands),'passing',len(good))
