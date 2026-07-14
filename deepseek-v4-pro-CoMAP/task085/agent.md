# Code Golf Task Guide

You are currently responsible for Task [85] in this code golf competition. The task data is available in the [data.json] file. Your goal is to write the shortest possible Python 3 file that includes an executable object named `p`. This object must correctly map each input matrix to its corresponding output matrix. All input and output values are integers between 0 and 9, structured as nested lists. Note: Third-party libraries such as `numpy` are not allowed, even though the local script currently does not check.

You can reference the `verify.py` script to understand how correctness is checked and code length is calculated. Length is measured by the total number of bytes in your final file. Equality between outputs is verified using `numpy.array_equal`, which means boolean values, floats, and other compatible types will be accepted as valid matches as long as their values align.

## First Priority: Study the Dataset Generator
The code that generates the `arc-gen` dataset split is located at [ARC-GEN-PATH]. All data in this split follows the exact logic defined in this generator. While the training and test splits may have slight variations from these rules, understanding how the generator creates the data is the single most important step to succeed at this task. Before you make any attempts to write code, take the time to fully read and analyze this generator file. It will reveal core patterns, edge cases, and hidden rules that you will never discover just by looking at sample input and output pairs. If you ever get stuck or feel like you're missing a key insight, return to the generator code to re-examine it—this will save you far more time than blindly trying different patterns.

## Explore Multiple Approaches in Parallel
Do not fixate on a single approach for too long. If one strategy is not yielding results, try completely different angles. You can use **the agent team feature** to run multiple distinct approaches at the same time. Test different logical patterns, syntax shortcuts, and implementation styles concurrently to quickly identify which directions are most promising. Don't let preconceived ideas limit you—the optimal solution for every task is shorter than you might expect. All tasks have a best solution under 100 bytes, and most are under 80 bytes.

## Map-and-Act Strategy: Build and Maintain a Cognitive Map

**Do not separate environment understanding from task execution.** Throughout your attempts to write, verify, and optimize code, you must **simultaneously build and maintain an internal cognitive map** of this task. This map should capture structured knowledge about the problem domain, and you should actively use it to guide your decisions instead of relying on blind trial‑and‑error. Specifically, your cognitive map must include the following categories:

- **Core logic of the data generator**: Key transformation rules, color mappings, shape constraints, boundary conditions, and any hidden invariants extracted from the generator code. Record concrete code snippets or pseudocode when possible.
- **Behavior of the verification script**: How `verify.py` checks correctness, measures byte length, and whether it performs implicit type conversions (e.g., accepting booleans or floats as valid matches). Note any special cases or edge conditions in the verification process.
- **Database of effective patterns**: All code patterns, Python language features (e.g., list comprehensions, `lambda`, `exec` tricks, bitwise operations) that have been proven to pass the tests, along with the exact byte count savings they provide.
- **Summary of failed attempts**: Detailed error messages, common pitfalls (e.g., off‑by‑one errors, type mismatches, incorrect handling of empty matrices), and the environmental constraints that caused them.
- **Byte‑count trends**: Record how much each successful optimization saved, and identify conflicts between optimizations (some combinations may unexpectedly increase length).

### How to Use Your Cognitive Map in Action

1. **Consult the map before each new attempt**: Review confirmed rules and discarded directions to avoid repeating mistakes. If a hypothesis is not yet recorded, run a small focused test to validate it and update the map before investing in a full solution.

2. **Update the map immediately after every verification run**: Whether the run passes or fails, extract new observations—error outputs, number of passing/failing cases, unexpected behavior—and distill them into structured entries in your progress log (e.g., `insights.md` inside `workdir/`).

3. **Leverage the map to guide parallel explorations**: When using the agent team to run multiple approaches, assign each team member a distinct hypothesis derived from your map (e.g., one focuses on color transformations, another on shape translations). Compare their verification results against the map to quickly filter the most promising routes.

4. **Use the map for strategic pivoting, not brute‑force searching**: If you spend multiple attempts on a path with no progress, step back and review the map for overlooked rules or high‑probability patterns that you have not yet exploited. Prioritize actions with the highest expected information gain based on your current knowledge.

5. **Keep the map concise and traceable**: The map is a distilled knowledge index, not a history log. Regularly prune outdated or irrelevant entries, and ensure each entry includes a short justification and, where applicable, a reproducible code snippet.

By adopting this **"map‑while‑act"** mindset, you will gradually build a deep, structured understanding of the task, minimize wasteful exploration, and converge faster toward the shortest valid solution.

## Prioritize Correctness and Optimize Incrementally
Correctness always comes before shortening your code. Do not try to apply every possible optimization all at once. **Start with a ungolfed, complete, working solution** that passes all test cases first. Once you have a valid implementation, apply one optimization at a time. After each change, run the full verification script to confirm your code still works correctly, measure exactly how many bytes you saved, and check that the change does not conflict with any other optimizations you have already made. Only move on to the next optimization once you have confirmed the current change is beneficial and does not break functionality. Never trade working correct code for shorter code that fails test cases.

## Working Requirements
- Work independently and choose the best approach for the task without asking for guidance
- All your work must be done inside the `workdir/` directory. Files outside this directory are read-only and cannot be modified. For each attempt you make, create a new Python file with a distinct name—do not overwrite or modify files from previous attempts.
- Always keep detailed records of your progress, insights, and conclusions inside the `workdir/` directory so you can learn from past attempts. Your records should include reproducible information, especially runnable code snippets. Regularly organize your work, remove outdated attempts, and keep summaries of what you have learned
- To verify correctness and measure code length, always use the official command: 'python3 verify.py <your-code>.py'. This is the only standard that counts for evaluation. Do not modify the verification files or use your own custom criteria to judge your code
- Never be overconfident in your assumptions. Test all data points and actually run your code to confirm it works. Record your results honestly—any false claims of progress will be immediately discovered when the verification script runs

Continue working autonomously until you achieve the shortest possible valid solution. Use your best judgment to make all decisions, and you do not need to ask for further confirmation as you work. **You must read the generator code first before any other actions. You must use the agent team feature to increase parallelism, avoid getting stuck in a single approach, and speed up the process. Please read and organize the current situation of the workdir as required, without doing any unnecessary repetitive work.**

## Format Requirements
You must maintain a version log for each attempt. Every log entry should clearly document the following:

Intuition: the reasoning or insight behind this specific change.

Rationale: why this approach is expected to work effectively.

Code: the full implementation code for that version.

Code-Length: the total character count or line count of the code.

Each log must be saved as a separate Markdown file, named using the convention version[i]-log.md (e.g., version1-log.md, version2-log.md, etc.).

Example (version[1]-log.md):

markdown
### version[1]-log.md

**Intuition:**
Removing all comments significantly reduces the total code length without altering the logic.

**Code-Length:**
2525

**Code:**
```python
def p(grid):
    # Shifts the top edge and left diagonal right by 1 pixel.
    height = len(grid)
    width = len(grid[0])

    pixels = set()
    for r in range(height):
        for c in range(width):
            if grid[r][c] != 0:
                pixels.add((r, c))

    components = []
    visited = set()

    for r, c in pixels:
        if (r, c) in visited:
            continue
        comp = set()
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if (cr, cc) in visited:
                continue
            visited.add((cr, cc))
            comp.add((cr, cc))
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < height and 0 <= nc < width:
                        if grid[nr][nc] != 0 and (nr, nc) not in visited:
                            stack.append((nr, nc))
        components.append(comp)

    output = [[0] * width for _ in range(height)]

    for comp in components:
        rows = {}
        for cr, cc in comp:
            rows.setdefault(cr, []).append(cc)

        min_row = min(rows)
        max_row = max(rows)
        overall_max_col = max(max(cols) for cols in rows.values())

        for cr, cols in rows.items():
            cols.sort()
            left_col = cols[0]
            right_col = cols[-1]

            if cr == min_row:
                for cc in cols:
                    if cc + 1 < width:
                        output[cr][cc + 1] = grid[cr][cc]
            elif cr == max_row:
                for cc in cols:
                    output[cr][cc] = grid[cr][cc]
            else:
                output[cr][left_col + 1] = grid[cr][left_col]
                if right_col < overall_max_col:
                    output[cr][right_col + 1] = grid[cr][right_col]
                else:
                    output[cr][right_col] = grid[cr][right_col]

    return output
