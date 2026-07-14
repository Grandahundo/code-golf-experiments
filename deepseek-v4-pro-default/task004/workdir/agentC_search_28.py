import sys, json, random, os, warnings
warnings.filterwarnings("ignore")
os.chdir('/Users/jackson/Desktop/code-golf/deepseek-v4-pro-default/task004')
sys.path.insert(0,'.')
from gen import validate
import gen
_D=validate(); _ARC=json.load(open('data.json'))['arc-gen']
random.seed(3); _RND=[gen.generate() for _ in range(250)]
def check(code):
    G={}
    try:
        exec(code,G); p=G['p']
        for s in('train','test'):
            for ex in _D[s]:
                if p(ex['input'])!=ex['output']: return False
        for e in _ARC:
            if p(e['input'])!=e['output']: return False
        for ex in _RND:
            if p(ex['input'])!=ex['output']: return False
    except Exception:
        return False
    return True
# stronger full-check for final confirmation of any hit
random.seed(7); _RND2=[gen.generate() for _ in range(4000)]
def full(code):
    G={}
    try:
        exec(code,G); p=G['p']
        for s in('train','test'):
            for ex in _D[s]:
                if p(ex['input'])!=ex['output']: return False
        for e in _ARC:
            if p(e['input'])!=e['output']: return False
        for ex in _RND+_RND2:
            if p(ex['input'])!=ex['output']: return False
    except Exception:
        return False
    return True

BASE=r"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]"
CHARS=list("abcgxyzuvw0123456789[]()+-<>*%:,. =")
KEYS=["any","max","min","sum","zip","range","len","for","in","if","else"]
found=[]; seen=set(); tested=0
def T(code):
    global tested
    if code in seen: return
    seen.add(code)
    if len(code)>=len(BASE): return
    tested+=1
    if check(code) and full(code):
        found.append((len(code),code)); print("HIT",len(code),repr(code),flush=True)
rnd=random.Random(2024)
def mutate(s):
    op=rnd.randrange(7); n=len(s)
    if n<6: return s
    if op==0: i=rnd.randrange(n); return s[:i]+s[i+1:]
    if op==1: i=rnd.randrange(n); return s[:i]+rnd.choice(CHARS)+s[i+1:]
    if op==2: i=rnd.randrange(n); return s[:i]+rnd.choice(CHARS)+s[i:]
    if op==3: i=rnd.randrange(n-1); return s[:i]+s[i+1]+s[i]+s[i+2:]
    if op==4:
        k=rnd.choice(KEYS)
        return s.replace(k,rnd.choice(KEYS),1) if k in s else s
    if op==5: i=rnd.randrange(n-1); return s[:i]+s[i+2:]
    if op==6: i=rnd.randrange(n-2); return s[:i]+s[i+3:]
    return s
N=40000
for it in range(N):
    s=BASE
    for _ in range(rnd.randrange(1,4)): s=mutate(s)
    T(s)
print("iters",N,"tested",tested)
found.sort()
print(found[:10] if found else "NOTHING < 82")
