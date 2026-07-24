You are an expert Python coder.

# Goal
Write a Python 3 program that defines a function `p` mapping each input grid to its corresponding output grid.

Rules:
- Grids are 2D nested lists of integers 0-9.
- `p` takes one argument (the input grid) and returns the output grid.
- Standard library only — third-party libraries such as numpy are NOT allowed.
- The examples are drawn from a common generation rule; `p` must implement the general rule, not memorize the examples.

# Output format
Reply with the final program in a single ```python code block. No explanation is needed outside the block.

# Task task006
Infer the transformation rule from the examples below, then implement it.

## Example 1  (input 3x7 -> output 3x3)
Input:
1 0 0 5 0 1 0
0 1 0 5 1 1 1
1 0 0 5 0 0 0
Output:
0 0 0
0 2 0
0 0 0

## Example 2  (input 3x7 -> output 3x3)
Input:
1 1 0 5 0 1 0
0 0 1 5 1 1 1
1 1 0 5 0 1 0
Output:
0 2 0
0 0 2
0 2 0

## Example 3  (input 3x7 -> output 3x3)
Input:
0 0 1 5 0 0 0
1 1 0 5 1 0 1
0 1 1 5 1 0 1
Output:
0 0 0
2 0 0
0 0 2