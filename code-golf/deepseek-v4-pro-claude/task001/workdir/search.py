import sys, importlib.util
sys.path.insert(0,'.')
from gen import validate
D=validate()
cases=[(e['input'],e['output']) for s in('train','test') for e in D[s]]

def ok(src):
    ns={}
    try:
        exec(src,ns)
        p=ns['p']
        return all(p([list(r) for r in inp])==out for inp,out in cases)
    except Exception as ex:
        return f"ERR:{ex}"

cands=[
 # baseline 61
 "p=lambda g:[[x&y for x in a for y in b]for a in g for b in g]",
 # commutative full swap
 "p=lambda g:[[x&y for y in b for x in a]for b in g for a in g]",
 # try 3-loop / index forms
 "p=lambda g,r=range(9):[[g[i//3][j//3]&g[i%3][j%3]for j in r]for i in r]",
 # sum-flatten variants
 "p=lambda g:[x&y for a in g for b in g for x in a for y in b]",
 # tile T & BV via zip (long, sanity)
 "p=lambda g:[[a&b for a,b in zip(x,y)]for x,y in zip([r*3for r in g*3],[[v for v in r for _ in g]for r in g for _ in g])]",
 # nested map ideas
 "p=lambda g:[[x&y for x in a for y in b]for a in g for b in g]",
]
for c in cands:
    print(len(c), ok(c), c[:70])
