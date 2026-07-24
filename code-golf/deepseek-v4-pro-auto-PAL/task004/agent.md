# Task 004 — Code Golf

Goal: shortest `p` function, target < 100 bytes.

## Quick start

```
1. Read gen.py — understand the transformation logic
2. Write code to workdir/v1.py
3. python3 verify.py workdir/v1.py
4. python3 status.py
5. Iterate: write → verify → write → verify
```

## This task

The generator produces parallelogram-shaped connected components and shifts their top edge and left diagonal right by 1 pixel. Input and output have identical dimensions. Colors are preserved.

Key observations from gen.py:
- Pixels are grouped into 8-directionally connected components
- Each component forms a parallelogram shape
- Top row of each component: shift every pixel right by 1
- Bottom row: stay in place
- Middle rows: left pixel shifts right by 1; right pixel shifts right by 1 unless at the component's rightmost column

Keep notes in `workdir/insights.md`. Stop when under 100 bytes.
