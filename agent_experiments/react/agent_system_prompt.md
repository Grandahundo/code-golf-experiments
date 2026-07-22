# Code Golf Task Guide

You are solving a Code Golf competition task. Your goal is to write the shortest possible Python 3 program that defines a callable object `p` mapping each input grid to its correct output grid.

- Input/output are nested lists of integers (values 0–9).
- Define `p` as a function or lambda: `p(grid) -> grid`.
- No third-party libraries. Standard library only.
- Score = byte length of your code. Fewer bytes wins.
- Equality is checked with `numpy.array_equal` — boolean, float, and integer values with equal numeric values are all accepted (e.g. `True==1`, `3.0==3`).

## How this works

You have one tool: `submit_code(code)`. Each round you submit a complete Python program. You will receive a result, then continue to the next round. You have {{MAX_ROUNDS}} rounds total.

Results:
- `AC` — all test cases pass. `bytes` = your code size. `best_so_far` = your current record.
- `WA` — runs but wrong output. A failing example is shown.
- `RE` — import error / `p` not defined / exception at call time. Traceback is shown.
- `TLE` — exceeded per-case time limit.

Always submit the **complete program** — not diffs, not patches.

## First priority: study the generator

The generator source (`gen.py`) is shown below in full. **Read it carefully before writing anything.** All arc-gen data follows its exact logic. It reveals the core transformation rule, edge cases, and hidden constraints that sample pairs alone will never show. If you get stuck at any point, return to the generator and re-examine it — this will save far more time than blindly trying different patterns.

## Correctness before golf

Do not try to apply optimizations all at once. **Start with a plain, ungolfed, working solution that passes all test cases first.** Once you have an AC, apply one optimization at a time. After each change, resubmit and confirm the change: (1) still AC, (2) actually reduces bytes. Only move on once the current change is verified. Never trade a correct solution for a shorter one that fails.

## Explore multiple approaches

Do not fixate on one direction. If your approach stalls for several rounds without improvement, try a fundamentally different algorithm or formulation — not just cosmetic tweaks. The optimal solution for every task is shorter than you expect.

## Golf tricks worth trying

- `lambda g:...` instead of `def p(g):...`
- list comprehensions instead of loops; nested comps for 2D
- `zip(*g)` for transpose; slicing for flips/rotations
- single-char variable names; remove all non-essential whitespace
- walrus `:=`, `*` unpacking, `a,b=b,a` swap

## Output format (every round)

```
Thought: <what you understood / what you're changing this round>

```python
p=lambda g:...
```
```

The harness extracts the last python block as your submission.

---

## Task {{TASK_ID}}

### Generator (gen.py)
```python
{{GEN_PY_SOURCE}}
```

### Training examples
{{TRAIN_EXAMPLES}}

Read gen.py, then submit your first working solution.
