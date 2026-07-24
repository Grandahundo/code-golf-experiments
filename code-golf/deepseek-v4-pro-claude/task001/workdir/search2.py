import sys
sys.path.insert(0,'.')
from gen import validate
D=validate()
cases=[(e['input'],e['output']) for s in('train','test') for e in D[s]]

def ok(src):
    ns={}
    try:
        exec(src,ns); p=ns['p']
        return all(p([list(r) for r in inp])==out for inp,out in cases)
    except Exception as ex:
        return f"ERR:{type(ex).__name__}"

C=[
 # reduce / sum flatten
 "p=lambda g:[r for a in g for r in[[x&y for x in a for y in b]for b in g]]",
 # zip outer product tricks
 "p=lambda g:[[x&y for x in a for y in b]for b in g for a in g]",   # partial swap (wrong?)
 # map based inner
 "p=lambda g:[[x&y for x in a for y in b]for a in g for b in g]",
 # sum with list mult, color-aware
 "p=lambda g:[sum([x*[y]or[0]for x in a],[])for a in g for b in g]",  # nonsense check
 # broadcast a, tile b
 "p=lambda g:[[m&t for m in a for t in b]for a in g for b in g]",
 # nested via product of enumerated - index
 "p=lambda g:[[g[i//3][k//3]&g[i%3][k%3]for k in a*3]for a in g for i in range(3)]",  # bogus
 # generator + chunk
 "p=lambda g:[[*t]for t in zip(*[iter(x&y for a in g for b in g for x in a for y in b)]*9)]",
 # tile & block-value both from g, via zip within band
 "p=lambda g:[[x&y for x,y in zip(a*3,b*3)]for a in g for b in g]",   # zip not cartesian (wrong)
 # the known-good
 "p=lambda g:[[x&y for x in a for y in b]for a in g for b in g]",
]
for c in C:
    print(len(c), ok(c), repr(c[:78]))
