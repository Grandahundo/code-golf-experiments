# Task 005 Insights

## Algorithm
1. Find middle anchor (R,C): densest 3x3 window in the 19x19 possible positions
2. For each non-zero pixel: compute direction d=(r-R)//4, e=(c-C)//4
3. Stamp the middle's sprite pattern along direction (d,e) at 4-step intervals
4. Use `common.draw()` for bounds-checked writes, `common.all_pixels()` for iteration

## Key insights
- Middle color is unique (excluded from direction colors) and has span (2,2) in both dims
- Direction can be computed directly: `d=(r-R)//4` gives correct floor division for all pixel positions
- Each direction stamp repeats every 4 cells from the middle
- Modifying input `g` in place via `draw(g,...)` saves allocating output grid

## Best: 357 bytes (v15)
- from common import* (18 bytes) — draw, grid, all_pixels save ~50 bytes total
- Density scan (79 bytes) — the irreducible bottleneck; finds middle via densest 3x3
- Per-pixel direction + stamp loop (~230 bytes) — stamps sprite along computed direction
- Remainder: function def, return, loop structure

## To reach <100 bytes
Would require fundamentally different approach that avoids the density scan entirely. Possible directions:
- Color-grouping with span heuristic (max-min==2 in both dims uniquely identifies middle)
- Exploiting mod-4 residue of all block anchors without scanning
- Direct mathematical mapping from input to output using grid-level operations
- The middle is the ONLY color where all pixels are within a 3x3 span in both dimensions
