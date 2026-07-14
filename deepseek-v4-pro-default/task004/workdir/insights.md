# Task 004 — SOLVED

## Final solution: workdir/best.py = 82 bytes (no trailing newline)
p=lambda g:[[a[c-(b[c-1]<any(b))]for c in range(len(a))]for a,b in zip(g,g[1:]+g)]

Verified: 3/3 validate (official verify.py, Code length 82), 262/262 arc-gen,
20000/20000 random gen.generate() (20 seeds). 0 failures.

## Rule
For row a and the row below b: out[c] = a[c-1] if b[c-1] < any(b) else a[c].
Index-arithmetic form: out[c] = a[c - (b[c-1] < any(b))]  (shift 0 or 1).
- any(b) = 0/1 gate: 0 => blank/bottom row (shift 0 => copy); 1 => shape continues below.
- The c=0 wrap (b[-1], a[-1]) is SAFE: whenever a[-1]!=0 (right cap at last col),
  the row below also has content there (b[-1]!=0 => shift 0) or is blank
  (any(b)=0 => shift 0); output col 0 is always 0. Proven by 20k random + arc-gen.

## Golf progression of the winning idea
86 (select form: [[y,x][u<any(b)]for x,y,u in zip([0]+a,a,[0]+b)]...) 
-> 82 (index-arith a[c-(b[c-1]<any(b))] over range(len(a)); avoids materializing
   two a-streams and the select brackets). range(len(a)) is the irreducible cost of c.

## Key facts (generator)
- Row g[0] always blank (shapes start at row=1) -> rotation zip(g,g[1:]+g) pairs the
  last row with the always-blank g[0] so it copies (shift 0). g[1:]+g is the shortest
  rotation (beats (g+g)[1:], (g*2)[1:], g[1:]+g[:1]).
- Output col 0 always 0. Each row has a single color (max(b) works as gate too, same len).
- Size history: 769->...->91->86->82.
