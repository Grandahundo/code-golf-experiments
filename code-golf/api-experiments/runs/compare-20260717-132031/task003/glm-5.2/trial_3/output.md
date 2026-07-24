```python
def p(grid):
    converted = [[2 if v == 1 else v for v in row] for row in grid]
    half = len(grid) // 2
    return converted + converted[:half]
```