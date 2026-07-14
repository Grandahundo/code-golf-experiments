#!/usr/bin/env python3
"""Quick status check. Usage: python3 status.py"""
import json, os

DAG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "workdir", "dag.json")

def render_tree(nodes):
    if not nodes:
        return "(empty)"
    roots = [n for n in nodes.values() if not n.get("parent") or n["parent"] not in nodes]
    lines = []
    def _render(n, prefix, last):
        conn = "└── " if last else "├── "
        tag = "✅" if n["passed"] else "❌"
        lines.append(f"{prefix}{conn}{tag} {n['version']} ({n['bytes']}b)")
        children = [c for c in nodes.values() if c.get("parent") == n["version"]]
        for i, c in enumerate(children):
            _render(c, prefix + ("    " if last else "│   "), i == len(children) - 1)
    for i, r in enumerate(roots):
        _render(r, "", i == len(roots) - 1)
    return "\n".join(lines)

def main():
    if not os.path.exists(DAG_PATH):
        print("no attempts yet — run: python3 verify.py workdir/v1.py")
        return

    with open(DAG_PATH) as f:
        dag = json.load(f)
    nodes = dag.get("nodes", {})
    if not nodes:
        print("no attempts yet")
        return

    passing = [n for n in nodes.values() if n["passed"]]
    failing = [n for n in nodes.values() if not n["passed"]]
    best = min(passing, key=lambda n: n["bytes"]) if passing else None

    print(f"{len(nodes)} attempts ({len(passing)} pass, {len(failing)} fail)")
    if best:
        print(f"best: {best['version']} — {best['bytes']} bytes")
    print()
    print(render_tree(nodes))
    if passing:
        sp = sorted(passing, key=lambda n: n.get("timestamp", ""))
        print(f"\ntrend: {' → '.join(str(n['bytes']) for n in sp)}")

if __name__ == "__main__":
    main()
