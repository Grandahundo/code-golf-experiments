import importlib.util
spec=importlib.util.spec_from_file_location('f','workdir/agentC_alt_fast.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
ok=f.fast_ok
cands=[
# baseline
"p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# ~- for c-1 in b index (same len) - sanity
"p=lambda g:[[a[c-(b[~-c]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# max instead of any (same len, works)
"p=lambda g:[[a[c-(b[c-1]<max(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# try enumerate value used to shorten: pick a[c-1] vs x
"p=lambda g:[[(a[c-1],x)[b[c-1]>=any(b)]for c,x in enumerate(a)]for a,b in zip(g,g[1:]+g)]",
# whole-index r,c with wrap %
"p=lambda g:[[a[c-(g[(r+1)%len(g)][c-1]<any(g[(r+1)%len(g)]))]for c in range(len(a))]for r,a in enumerate(g)]",
# below via slicing d, pair with zip, use d[c-1]
# use b and a zipped, prepend 0, index by running? no
# gate with b.count trick (single color)
"p=lambda g:[[a[c-(0<any(b)>b[c-1])]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
# multiply any(b) into subtraction, factor
"p=lambda g:[[a[c-any(b)+b[c-1].__gt__(0)*any(b)]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]",
]
for cstr in cands:
    print(len(cstr), 'OK' if ok(cstr) else 'FAIL')
