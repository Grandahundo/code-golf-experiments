def p(grid):
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    entries = []
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 0:
                entries.append((r + c, grid[r][c]))

    for period in range(1, rows + cols):
        pattern_map = {}
        consistent = True
        for s, val in entries:
            idx = s % period
            if idx in pattern_map:
                if pattern_map[idx] != val:
                    consistent = False
                    break
            else:
                pattern_map[idx] = val

        if consistent and len(pattern_map) == period:
            pattern = [pattern_map[i] for i in range(period)]
            output = []
            for r in range(rows):
                row = []
                for c in range(cols):
                    row.append(pattern[(r + c) % period])
                output.append(row)
            return output

    return grid
