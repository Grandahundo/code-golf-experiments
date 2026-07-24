def p(g):
    s=len(g)
    return [[g[R%s][C%s] if g[R//s][C//s] else 0 for C in range(s*s)] for R in range(s*s)]
