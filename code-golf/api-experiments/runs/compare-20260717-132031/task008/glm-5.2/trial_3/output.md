```python
def p(grid):
    h = len(grid)
    w = len(grid[0]) if h else 0

    red = []
    az = []
    for r in range(h):
        row = grid[r]
        for c in range(w):
            v = row[c]
            if v == 2:
                red.append((r, c))
            elif v == 8:
                az.append((r, c))

    if not red or not az:
        return [row[:] for row in grid]

    az_set = set(az)
    near = set()
    for r, c in az:
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < h and 0 <= nc < w and (nr, nc) not in az_set:
                near.add((nr, nc))

    n = len(red)
    m = len(az)
    s_red_r = sum(r for r, c in red)
    s_red_c = sum(c for r, c in red)
    s_az_r = sum(r for r, c in az)
    s_az_c = sum(c for r, c in az)
    vr = s_az_r * n - s_red_r * m
    vc = s_az_c * n - s_red_c * m

    rmin = min(r for r, c in red)
    rmax = max(r for r, c in red)
    cmin = min(c for r, c in red)
    cmax = max(c for r, c in red)

    ar0 = min(r for r, c in az)
    ar1 = max(r for r, c in az)
    ac0 = min(c for r, c in az)
    ac1 = max(c for r, c in az)

    if rmax < ar0:
        gap_v = ar0 - rmax - 1
    elif rmin > ar1:
        gap_v = rmin - ar1 - 1
    else:
        gap_v = 0

    if cmax < ac0:
        gap_h = ac0 - cmax - 1
    elif cmin > ac1:
        gap_h = cmin - ac1 - 1
    else:
        gap_h = 0

    if gap_v > gap_h:
        pref_side = 0
    elif gap_h > gap_v:
        pref_side = 1
    else:
        pref_side = -1

    best = None
    best_key = None

    for dr in range(-rmin, h - rmax):
        for dc in range(-cmin, w - cmax):
            dist = abs(dr) + abs(dc)
            if best_key is not None and dist > best_key[0]:
                continue

            overlap = False
            adj = False
            for r, c in red:
                pos = (r + dr, c + dc)
                if pos in az_set:
                    overlap = True
                    break
                if pos in near:
                    adj = True

            if overlap or not adj:
                continue

            nr0 = rmin + dr
            nr1 = rmax + dr
            nc0 = cmin + dc
            nc1 = cmax + dc

            if (nr1 + 1 == ar0 or nr0 == ar1 + 1) and nc1 >= ac0 and nc0 <= ac1:
                side = 0
            elif (nc1 + 1 == ac0 or nc0 == ac1 + 1) and nr1 >= ar0 and nr0 <= ar1:
                side = 1
            else:
                side = 2

            side_pref = 0 if (pref_side == -1 or side == pref_side) else 1
            dot = dr * vr + dc * vc
            both = 0 if (dr == 0 or dc == 0) else 1
            key = (dist, side_pref, -dot, both, abs(dr), abs(dc))

            if best_key is None or key < best_key:
                best_key = key
                best = (dr, dc)

    if best is None:
        return [row[:] for row in grid]

    dr, dc = best
    out = [row[:] for row in grid]
    for r, c in red:
        out[r][c] = 0
    for r, c in red:
        out[r + dr][c + dc] = 2
    return out
```