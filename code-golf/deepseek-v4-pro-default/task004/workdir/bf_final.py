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

C=[]
# range starting at 1 with [0]+ prefix (col0 always 0)
C.append('p=lambda g:[[0]+[a[c-(b[c-1]<any(b))]for c in range(1,len(a))]for a,b in zip(g,g[1:]+g)]')
# def with prepend-0-col preprocessing then strip
C.append('def p(g):\n h=[[0]+r for r in g]\n return[[a[c-(b[c-1]<any(b))]for c in range(len(a))][1:]for a,b in zip(h,h[1:]+h)]')
# map over rows
C.append('p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')
# global shift: build shifted grid S (each row right-shift), pick per cell
C.append('p=lambda g:[[[a[c],a[c-1]][b[c-1]<any(b)]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')
# use s=[0]+a shifted row via walrus per row, then select
C.append('p=lambda g:[[(s:=[0]+a)[c]if b[c-1]<any(b)else a[c]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]')
# nested: define blank via *g wrap alt
C.append('p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,[*g[1:],*g])]')
# using g[1:]+g[:1]
C.append('p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g[:1])]')
# last row appended unchanged, zip(g,g[1:])
C.append('p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:])]+[g[-1]]')
# enumerate with x value reused for keep
C.append('p=lambda g:[[a[c-1]if b[c-1]<any(b)else x for c,x in enumerate(a)]for a,b in zip(g,g[1:]+g)]')

for s in C:
    print(test(s), len(s), repr(s))
best=[ (len(s),s) for s in C if test(s)]
best.sort()
print('\nbest passing:',best[0] if best else None)
under=[b for b in best if b[0]<82]
print('UNDER 82:',under)
