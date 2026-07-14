#!/usr/bin/env python3
"""
verify.py — Verification entry point (framework wrapper).

Usage (identical to original):
    python3 verify.py <file.py>

What happens:
    1. Runs the real verification (_verify_impl.py)
    2. Auto-infers parent version by code similarity
    3. Records every attempt in the DAG — pass AND fail
    4. Displays version tree and trend
    5. Persists everything to workdir/
"""
import sys, os, json, difflib, hashlib, subprocess
from datetime import datetime

TASK_DIR = os.path.dirname(os.path.abspath(__file__))
WORKDIR = os.path.join(TASK_DIR, "workdir")
DAG_PATH = os.path.join(WORKDIR, "dag.json")
IMPL = os.path.join(TASK_DIR, "_verify_impl.py")

# ── DAG ──
def load_dag():
    if os.path.exists(DAG_PATH):
        with open(DAG_PATH) as f:
            return json.load(f)
    return {"nodes": {}}

def save_dag(dag):
    os.makedirs(WORKDIR, exist_ok=True)
    dag["updated"] = datetime.now().isoformat()
    with open(DAG_PATH, "w") as f:
        json.dump(dag, f, indent=2)

# ── Similarity ──
def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def infer_parent(code, dag):
    nodes = dag.get("nodes", {})
    if not nodes:
        return None, 0.0
    best_v, best_s = None, 0.0
    for vid, n in nodes.items():
        s = similarity(code, n["code"])
        if s > best_s:
            best_s, best_v = s, vid
    return (best_v, best_s) if best_s >= 0.3 else (None, best_s)

# ── Bytes ──
def extract_bytes(stdout):
    for line in stdout.split("\n"):
        if "code length:" in line.lower():
            try:
                return int(line.split(":")[1].strip().split()[0])
            except (IndexError, ValueError):
                pass
    return 0

# ── Tree ──
def render_tree(nodes):
    """Return ASCII tree string."""
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

# ── Main ──
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 verify.py <file.py>")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        sys.exit(1)

    with open(filepath) as f:
        code = f.read()
    code_hash = hashlib.sha256(code.encode()).hexdigest()[:12]

    # 1. Run real verification
    r = subprocess.run([sys.executable, IMPL, filepath],
                       capture_output=True, text=True, timeout=30, cwd=TASK_DIR)
    stdout = r.stdout
    passed = "Failed: 0" in stdout
    byte_count = extract_bytes(stdout)
    print(stdout)

    # 2. Load DAG, dedup
    dag = load_dag()
    for n in dag.get("nodes", {}).values():
        if n.get("code_hash") == code_hash:
            print(f"[*] already recorded as {n['version']}  "
                  f"parent={n.get('parent','root')}  {'✅' if n['passed'] else '❌'}")
            return

    # 3. Infer parent
    parent, sim = infer_parent(code, dag)

    # 4. Record
    version = f"v{len(dag['nodes']) + 1}"
    dag["nodes"][version] = {
        "version": version,
        "parent": parent,
        "code": code,
        "bytes": byte_count,
        "passed": passed,
        "code_hash": code_hash,
        "file": os.path.basename(filepath),
        "timestamp": datetime.now().isoformat(),
    }
    save_dag(dag)

    # 5. Summary
    passing = [n for n in dag["nodes"].values() if n["passed"]]
    best = min(passing, key=lambda n: n["bytes"]) if passing else None
    sim_str = f"sim:{sim:.0%}" if parent else "new branch"

    print(f"[*] {version}  parent:{parent or 'root'}  {sim_str}  "
          f"{'✅' if passed else '❌'}  {byte_count}b")
    print(f"[*] {len(dag['nodes'])} attempts | {len(passing)} pass | "
          f"best:{best['bytes'] if best else 'N/A'}b")
    print(f"[*] tree:")
    print(render_tree(dag["nodes"]))

if __name__ == "__main__":
    main()
