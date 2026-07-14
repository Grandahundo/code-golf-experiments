import sys
sys.path.insert(0,'..')
from gen import validate
from verify import load_p

p = load_p('v_rec1.py')
data = validate()
results = []
for split in ("train","test"):
    for i, ex in enumerate(data[split]):
        try:
            got = p(ex["input"])
            ok = got == ex["output"]
            results.append(f"[{split} {i}] {'PASS' if ok else 'FAIL'}")
            if not ok:
                print(f"FAIL at {split} {i}")
        except Exception as e:
            results.append(f"[{split} {i}] ERROR: {e}")
            print(f"ERROR at {split} {i}: {e}")
for r in results:
    print(r)
print("All passed:", all("PASS" in r for r in results))
