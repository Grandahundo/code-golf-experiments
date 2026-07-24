You are an expert Python coder.

# Goal
Write the SHORTEST possible Python 3 program that defines a function `p` mapping each input grid to its corresponding output grid.

Rules:
- Grids are 2D nested lists of integers 0-9.
- `p` takes one argument (the input grid) and returns the output grid.
- Standard library only — third-party libraries such as numpy are NOT allowed.
- Score = byte length of the program. Shorter is better, but the code MUST be correct first.
- The examples are drawn from a common generation rule; `p` must implement the general rule, not memorize the examples.

# Output format
Reply with the final program in a single ```python code block. No explanation is needed outside the block.

# Task task007
Infer the transformation rule from the examples below, then implement it.

## Example 1  (input 7x7 -> output 7x7)
Input:
2 8 3 0 0 0 0
8 3 0 0 0 0 0
3 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 0
Output:
2 8 3 2 8 3 2
8 3 2 8 3 2 8
3 2 8 3 2 8 3
2 8 3 2 8 3 2
8 3 2 8 3 2 8
3 2 8 3 2 8 3
2 8 3 2 8 3 2

## Example 2  (input 7x7 -> output 7x7)
Input:
0 0 0 0 0 0 0
0 0 0 0 0 0 0
0 0 0 0 0 0 1
0 0 0 0 0 1 2
0 0 0 0 1 2 4
0 0 0 1 2 4 0
0 0 1 2 4 0 0
Output:
2 4 1 2 4 1 2
4 1 2 4 1 2 4
1 2 4 1 2 4 1
2 4 1 2 4 1 2
4 1 2 4 1 2 4
1 2 4 1 2 4 1
2 4 1 2 4 1 2

## Example 3  (input 7x7 -> output 7x7)
Input:
0 0 0 0 8 3 0
0 0 0 8 3 0 0
0 0 8 3 0 0 0
0 8 3 0 0 0 4
8 3 0 0 0 4 0
3 0 0 0 4 0 0
0 0 0 4 0 0 0
Output:
4 8 3 4 8 3 4
8 3 4 8 3 4 8
3 4 8 3 4 8 3
4 8 3 4 8 3 4
8 3 4 8 3 4 8
3 4 8 3 4 8 3
4 8 3 4 8 3 4