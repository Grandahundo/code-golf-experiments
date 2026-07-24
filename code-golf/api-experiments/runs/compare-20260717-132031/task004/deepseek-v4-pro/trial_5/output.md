```python
from typing import List

def p(grid: List[List[int]]) -> List[List[int]]:
    H = len(grid)
    W = len(grid[0])
    # Collect all distinct non-zero values
    values = set()
    for r in range(H):
        for c in range(W):
            if grid[r][c] != 0:
                values.add(grid[r][c])
    
    # Initialize output grid with zeros
    output = [[0] * W for _ in range(H)]
    
    # Process each value independently
    for v in values:
        # Determine the rightmost column occupied by value v in the original grid
        max_col = -1
        for r in range(H):
            for c in range(W):
                if grid[r][c] == v and c > max_col:
                    max_col = c
        
        # Apply movement rule row by row
        for r in range(H):
            c = 0
            while c < W:
                if grid[r][c] == v:
                    start = c
                    # Find the contiguous horizontal run of v
                    while c < W and grid[r][c] == v:
                        c += 1
                    end = c - 1
                    target = end + 1  # column to the right of the segment
                    
                    # The segment shifts right by one if:
                    # - target is within the grid bounds
                    # - target does not exceed the maximum column of this value
                    # - the target cell is empty in the original grid
                    if target < W and target <= max_col and grid[r][target] == 0:
                        # Shift the segment
                        for col in range(start, end + 1):
                            output[r][col + 1] = v
                    else:
                        # Leave the segment in place
                        for col in range(start, end + 1):
                            output[r][col] = v
                else:
                    c += 1
                    
    return output
```