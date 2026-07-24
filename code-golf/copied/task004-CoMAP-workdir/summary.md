# Task 004 Summary

## Best Solution: v37, 128 bytes
```python
def p(g):
 for r,b in zip(g,g[1:]):
  for c,v in[*enumerate(r)][::-1]:
   if v*(c<bytearray(b).rfind(v)):r[c:c+2]=0,v
 return g
```

## Progression
- v1: 309 bytes (two-pass per-color, ungolfed)
- v5: 249 bytes (single-pass bottom-up, list-based arrays)
- v9: 181 bytes ([*enumerate] trick for reversed iteration)
- v19: 178 bytes (single dict D mapping color→(row,col))
- v23: 174 bytes (D.get for first-occurrence)
- v25: 171 bytes (slice assignment r[c:c+2]=0,v)
- v29: 156 bytes (zip(g,g[1:]) top-to-bottom approach)
- v35: 140 bytes (inline ''join(map(str)) instead of dict comp)
- v36: 133 bytes (bytes.rfind instead of str.rfind)
- v37: 128 bytes (bytearray.rfind with int arg)

## Key Insights
1. Each shape has unique color → per-color = per-shape
2. Bottom row pixels stay, others shift right (clamped to max_col)
3. Max_col can be found from row below: `bytearray(b).rfind(v)`
4. No persistent state needed — each row pair is independent
5. Right-to-left processing avoids overwrite conflicts
