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

# Task task001
Infer the transformation rule from the examples below, then implement it.

## Example 1  (input 3x3 -> output 9x9)
Input:
0 7 7
7 7 7
0 7 7
Output:
0 0 0 0 7 7 0 7 7
0 0 0 7 7 7 7 7 7
0 0 0 0 7 7 0 7 7
0 7 7 0 7 7 0 7 7
7 7 7 7 7 7 7 7 7
0 7 7 0 7 7 0 7 7
0 0 0 0 7 7 0 7 7
0 0 0 7 7 7 7 7 7
0 0 0 0 7 7 0 7 7

## Example 2  (input 3x3 -> output 9x9)
Input:
4 0 4
0 0 0
0 4 0
Output:
4 0 4 0 0 0 4 0 4
0 0 0 0 0 0 0 0 0
0 4 0 0 0 0 0 4 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 4 0 4 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 4 0 0 0 0

## Example 3  (input 3x3 -> output 9x9)
Input:
0 0 0
0 0 2
2 0 2
Output:
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 2
0 0 0 0 0 0 2 0 2
0 0 0 0 0 0 0 0 0
0 0 2 0 0 0 0 0 2
2 0 2 0 0 0 2 0 2

## Example 4  (input 3x3 -> output 9x9)
Input:
6 6 0
6 0 0
0 6 6
Output:
6 6 0 6 6 0 0 0 0
6 0 0 6 0 0 0 0 0
0 6 6 0 6 6 0 0 0
6 6 0 0 0 0 0 0 0
6 0 0 0 0 0 0 0 0
0 6 6 0 0 0 0 0 0
0 0 0 6 6 0 6 6 0
0 0 0 6 0 0 6 0 0
0 0 0 0 6 6 0 6 6

## Example 5  (input 3x3 -> output 9x9)
Input:
2 2 2
0 0 0
0 2 2
Output:
2 2 2 2 2 2 2 2 2
0 0 0 0 0 0 0 0 0
0 2 2 0 2 2 0 2 2
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
0 0 0 2 2 2 2 2 2
0 0 0 0 0 0 0 0 0
0 0 0 0 2 2 0 2 2