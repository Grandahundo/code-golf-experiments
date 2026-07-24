def p(grid):
    # Replace all 1s with 2s
    transformed = [[2 if x == 1 else x for x in row] for row in grid]
    n = len(transformed)
    target = n + n // 2  # e.g., 6 -> 9

    # Find the shortest repeating period of the row sequence
    period = n
    for p in range(1, n + 1):
        if all(transformed[i] == transformed[i + p] for i in range(n - p)):
            period = p
            break

    # Extend the grid to the target number of rows using the periodic pattern
    result = [row[:] for row in transformed]
    for i in range(n, target):
        result.append(transformed[i % period][:])

    return result
