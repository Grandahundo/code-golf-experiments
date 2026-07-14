import sys, json, random
sys.path.insert(0, '.')
from gen import validate
import gen
def check(code):
    G={};exec(code,G);p=G['p']
    d=validate()
    for s in('train','test'):
        for ex in d[s]:
            if p(ex['input'])!=ex['output']:return False,'validate'
    for e in json.load(open('data.json'))['arc-gen']:
        if p(e['input'])!=e['output']:return False,'arcgen'
    random.seed(3)
    for _ in range(2000):
        ex=gen.generate()
        if p(ex['input'])!=ex['output']:return False,'random'
    return True,len(code)
if __name__=='__main__':
    ok,info=check(sys.argv[1]);print('bytes',len(sys.argv[1]),'OK' if ok else 'FAIL',info)
