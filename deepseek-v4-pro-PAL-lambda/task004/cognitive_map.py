#!/usr/bin/env python3
"""
PAL-style Cognitive Map for Code Golf
=====================================
This is NOT prose for the LLM to read and ignore.
This IS the executable skeleton that:
  1. Defines structured knowledge (typed fields, not free text)
  2. Enforces a state machine (LLM cannot skip steps)
  3. Maintains a version DAG (branching optimization paths)
  4. Auto-verifies every attempt (constraints as code, not "please remember to...")
  5. Logs everything to disk (survives context truncation)

The LLM's job: read this module → extend knowledge → write candidate.py → call verify()
The framework's job: enforce transitions, log results, maintain the DAG, prevent cheating
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict, List, Set, Tuple, Any, Union
import json
import os
import subprocess
import sys
import hashlib
from datetime import datetime
from pathlib import Path


# ╔══════════════════════════════════════════════════════════════╗
# ║  1. STRUCTURED TASK KNOWLEDGE (typed, not "please note")    ║
# ╚══════════════════════════════════════════════════════════════╝

@dataclass
class GridSpec:
    """Structured description of input/output grid properties."""
    height: int
    width: int
    colors_present: Set[int] = field(default_factory=set)
    colors_output: Set[int] = field(default_factory=set)
    is_square: bool = False
    value_range: Tuple[int, int] = (0, 9)

    @classmethod
    def from_grid(cls, grid: List[List[int]]) -> "GridSpec":
        h, w = len(grid), len(grid[0])
        colors = {cell for row in grid for cell in row}
        return cls(height=h, width=w, colors_present=colors,
                   is_square=(h == w))


@dataclass
class TaskKnowledge:
    """
    Accumulated structured knowledge about this task.
    Every field is typed — LLM must fill these, not write essays.
    """
    # Geometry
    input_spec: Optional[GridSpec] = None
    output_spec: Optional[GridSpec] = None

    # Transformation (fill as you discover)
    transformation_type: str = ""             # e.g. "shift", "scale", "flood_fill"
    transformation_params: Dict[str, Any] = field(default_factory=dict)  # e.g. {"delta": 1}

    # Invariants — things that NEVER change between input and output
    invariants: List[str] = field(default_factory=list)
    # e.g. "grid dimensions unchanged", "color set unchanged"

    # Discovered rules (fill incrementally)
    rules: List[str] = field(default_factory=list)
    # e.g. "connected components shift right by 1 on top edge"

    # Edge cases found in data
    edge_cases: List[str] = field(default_factory=list)
    # e.g. "empty grid → empty grid", "single pixel → no shift"

    # Confidence in current understanding (0.0 - 1.0)
    confidence: float = 0.0

    def to_markdown(self) -> str:
        """Export as readable summary (for human inspection, not for LLM context)."""
        lines = ["# Task Knowledge", ""]
        if self.input_spec:
            lines.append(f"- **Input**: {self.input_spec.height}×{self.input_spec.width}, "
                        f"colors={self.input_spec.colors_present}")
        if self.output_spec:
            lines.append(f"- **Output**: {self.output_spec.height}×{self.output_spec.width}, "
                        f"colors={self.output_spec.colors_output}")
        lines.append(f"- **Type**: {self.transformation_type}")
        lines.append(f"- **Params**: {self.transformation_params}")
        lines.append(f"- **Confidence**: {self.confidence:.0%}")
        if self.invariants:
            lines.append(f"- **Invariants**: {self.invariants}")
        if self.rules:
            lines.append("\n## Rules")
            for r in self.rules:
                lines.append(f"- {r}")
        if self.edge_cases:
            lines.append("\n## Edge Cases")
            for e in self.edge_cases:
                lines.append(f"- {e}")
        return "\n".join(lines)


# ╔══════════════════════════════════════════════════════════════╗
# ║  2. STATE MACHINE (LLM cannot skip or reorder)              ║
# ╚══════════════════════════════════════════════════════════════╝

class GolfState(Enum):
    """
    Allowed states for the code golf agent.
    The LLM can ONLY operate within the current state's allowed actions.
    """
    INIT           = "init"            # Fresh start, nothing done yet
    ANALYZE_GEN    = "analyze_gen"     # Reading gen.py to understand transformation
    ANALYZE_DATA   = "analyze_data"    # Examining specific input/output pairs
    WRITE_CODE     = "write_code"      # Writing candidate.py
    VERIFY         = "verify"          # Running verify.py
    GOLF           = "golf"            # Optimizing (code passes, now shrink it)
    DONE           = "done"            # Target reached (under 100 bytes)


# Allowed transitions — centralized, single source of truth
STATE_TRANSITIONS: Dict[GolfState, List[GolfState]] = {
    GolfState.INIT:          [GolfState.ANALYZE_GEN],
    GolfState.ANALYZE_GEN:   [GolfState.ANALYZE_DATA, GolfState.WRITE_CODE],
    GolfState.ANALYZE_DATA:  [GolfState.WRITE_CODE, GolfState.ANALYZE_GEN],
    GolfState.WRITE_CODE:    [GolfState.VERIFY],
    GolfState.VERIFY:        [GolfState.GOLF, GolfState.WRITE_CODE, GolfState.ANALYZE_GEN],
    GolfState.GOLF:          [GolfState.VERIFY, GolfState.WRITE_CODE],
    GolfState.DONE:          [],  # Terminal state
}


class StateGuard:
    """
    Enforces state transitions. Call before any LLM action.
    Raises AssertionError if the LLM tries to skip steps.
    """
    def __init__(self):
        self.current_state = GolfState.INIT

    def can_transition_to(self, target: GolfState) -> bool:
        return target in STATE_TRANSITIONS.get(self.current_state, [])

    def transition_to(self, target: GolfState) -> bool:
        if self.current_state == target:
            return True  # already there, no-op
        if not self.can_transition_to(target):
            allowed = [s.value for s in STATE_TRANSITIONS.get(self.current_state, [])]
            raise AssertionError(
                f"⛔ 非法状态转换: {self.current_state.value} → {target.value}\n"
                f"   允许的下一步: {allowed}\n"
                f"   你跳步骤了！必须先完成当前阶段。"
            )
        self.current_state = target
        return True

    def allowed_actions(self) -> List[str]:
        """What the LLM is allowed to do right now."""
        return [s.value for s in STATE_TRANSITIONS.get(self.current_state, [])]


# ╔══════════════════════════════════════════════════════════════╗
# ║  3. VERSION DAG (tree of optimization paths)                ║
# ╚══════════════════════════════════════════════════════════════╝

@dataclass
class Attempt:
    """
    One attempt = one candidate.py file. Forms a node in the DAG.
    Each attempt has a parent (which version it branched from),
    enabling tree exploration and parallel optimization paths.
    """
    version: str                      # e.g. "v1", "v2a", "v2b"
    parent: Optional[str]             # parent version (None for root)
    code: str                         # full Python source
    bytes: int                        # code length
    passed: bool                      # did verify.py pass?
    test_results: Dict[str, Any] = field(default_factory=dict)  # parsed verify output
    insight: str = ""                 # what was changed and why
    expected_saving: int = 0          # expected byte saving (may differ from actual)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    code_hash: str = ""               # sha256 of code (dedup)

    def __post_init__(self):
        if not self.code_hash:
            self.code_hash = hashlib.sha256(self.code.encode()).hexdigest()[:12]


class VersionDAG:
    """
    DAG (actually a tree since each node has exactly one parent) of all attempts.
    Supports branching: from any working version, spawn multiple optimization
    strategies as sibling branches.
    """
    def __init__(self, save_path: str = "workdir/dag.json"):
        self.nodes: Dict[str, Attempt] = {}
        self.save_path = save_path
        self._load()

    def _load(self):
        """Load existing DAG from disk (survives context truncation)."""
        if os.path.exists(self.save_path):
            with open(self.save_path) as f:
                data = json.load(f)
                for v_id, node_data in data.get("nodes", {}).items():
                    self.nodes[v_id] = Attempt(**node_data)

    def save(self):
        """Persist DAG to disk."""
        data = {
            "nodes": {vid: asdict(n) for vid, n in self.nodes.items()},
            "last_updated": datetime.now().isoformat(),
        }
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
        with open(self.save_path, "w") as f:
            json.dump(data, f, indent=2)

    def next_version(self, parent: Optional[str] = None) -> str:
        """Generate next version ID, globally unique."""
        return f"v{len(self.nodes) + 1}"

    def add(self, attempt: Attempt):
        """Add a node to the DAG. Auto-saves."""
        if attempt.version in self.nodes:
            raise ValueError(f"Version {attempt.version} already exists")
        self.nodes[attempt.version] = attempt
        self.save()

    def get(self, version: str) -> Optional[Attempt]:
        return self.nodes.get(version)

    def best(self) -> Optional[Attempt]:
        """Return the shortest passing attempt."""
        passing = [n for n in self.nodes.values() if n.passed]
        if not passing:
            return None
        return min(passing, key=lambda n: n.bytes)

    def chain(self, version: str) -> List[Attempt]:
        """Follow parents back to root, returning the full chain."""
        chain = []
        current = self.nodes.get(version)
        while current:
            chain.append(current)
            current = self.nodes.get(current.parent) if current.parent else None
        return list(reversed(chain))

    def branches(self) -> Dict[str, List[Attempt]]:
        """Group nodes by their root-level branching point."""
        roots = [n for n in self.nodes.values() if n.parent is None]
        result = {}
        for root in roots:
            descendants = [n for n in self.nodes.values()
                          if self._is_descendant(n.version, root.version)]
            if len(descendants) > 1:  # Only report actual branches
                result[root.version] = descendants
        return result

    def _is_descendant(self, version: str, ancestor: str) -> bool:
        """Check if version is a descendant of ancestor."""
        current = self.nodes.get(version)
        while current:
            if current.version == ancestor:
                return True
            current = self.nodes.get(current.parent) if current.parent else None
        return False

    def trend(self) -> List[Tuple[str, int]]:
        """Return [(version, bytes)] sorted by insertion order for the best chain."""
        best = self.best()
        if not best:
            return []
        return [(n.version, n.bytes) for n in self.chain(best.version)]

    def stats(self) -> Dict[str, Any]:
        """Summary statistics."""
        all_nodes = list(self.nodes.values())
        passing = [n for n in all_nodes if n.passed]
        return {
            "total_attempts": len(all_nodes),
            "passing_attempts": len(passing),
            "best_bytes": self.best().bytes if self.best() else None,
            "unique_strategies": len(self.branches()),
            "total_bytes_saved": (
                all_nodes[0].bytes - self.best().bytes
                if all_nodes and self.best() else 0
            ),
        }

    # ── ASCII Tree Visualization ──
    def ascii_tree(self) -> str:
        """Render the DAG as an ASCII tree for quick visual inspection."""
        if not self.nodes:
            return "(empty)"

        roots = [n for n in self.nodes.values() if n.parent is None]
        lines = []

        def _render(node: Attempt, prefix: str, is_last: bool):
            connector = "└── " if is_last else "├── "
            status = "✅" if node.passed else "❌"
            lines.append(f"{prefix}{connector}{status} {node.version} ({node.bytes}b) "
                        f"— {node.insight[:50]}")
            children = [n for n in self.nodes.values() if n.parent == node.version]
            for i, child in enumerate(children):
                child_prefix = prefix + ("    " if is_last else "│   ")
                _render(child, child_prefix, i == len(children) - 1)

        for i, root in enumerate(roots):
            _render(root, "", i == len(roots) - 1)

        return "\n".join(lines)


# ╔══════════════════════════════════════════════════════════════╗
# ║  4. CONSTRAINT ENFORCEMENT (code, not "please remember")    ║
# ╚══════════════════════════════════════════════════════════════╝

class ConstraintViolation(Exception):
    """Raised when LLM violates a hard constraint. Names the specific rule broken."""
    pass


def enforce_all(code: str) -> None:
    """
    Check ALL constraints on candidate code.
    Each check raises ConstraintViolation with a specific message.
    LLM must fix the violation before verify() will run.
    """
    checks = [
        _check_has_p_function,
        _check_no_forbidden_imports,
        _check_valid_syntax,
        _check_no_file_io,
    ]
    violations = []
    for check in checks:
        try:
            check(code)
        except ConstraintViolation as e:
            violations.append(str(e))

    if violations:
        raise ConstraintViolation(
            "以下约束被违反:\n  - " + "\n  - ".join(violations)
        )


def _check_has_p_function(code: str):
    if "def p(" not in code and "p=lambda" not in code:
        raise ConstraintViolation("必须定义 'p' 函数 (def p 或 p=lambda)")


def _check_no_forbidden_imports(code: str):
    forbidden = ["import numpy", "from numpy", "import scipy", "import torch",
                 "import tensorflow"]
    for f in forbidden:
        if f in code:
            raise ConstraintViolation(f"禁止使用第三方库: {f}")


def _check_valid_syntax(code: str):
    try:
        compile(code, "<candidate>", "exec")
    except SyntaxError as e:
        raise ConstraintViolation(f"Python 语法错误: {e}")


def _check_no_file_io(code: str):
    for keyword in ["open(", "__file__", "os.system", "subprocess"]:
        if keyword in code:
            raise ConstraintViolation(f"禁止文件/系统操作: {keyword}")


# ╔══════════════════════════════════════════════════════════════╗
# ║  5. VERIFICATION RUNNER                                     ║
# ╚══════════════════════════════════════════════════════════════╝

def verify(code: str, task_dir: str = ".") -> Attempt:
    """
    Run verify.py against candidate code. Returns a structured Attempt.
    This is THE ONLY way to create a verified attempt — no bypassing.
    """
    # 1. Enforce constraints
    enforce_all(code)

    # 2. Write candidate to temp file
    candidate_path = os.path.join(task_dir, "_candidate.py")
    with open(candidate_path, "w") as f:
        f.write(code)

    # 3. Run verify.py
    try:
        result = subprocess.run(
            [sys.executable, "verify.py", candidate_path],
            capture_output=True, text=True,
            timeout=30,
            cwd=task_dir,
        )
    except subprocess.TimeoutExpired:
        result = subprocess.CompletedProcess([], 1, "", "Timeout (30s)")
    finally:
        # Cleanup temp
        if os.path.exists(candidate_path):
            os.remove(candidate_path)

    # 4. Parse output
    stdout = result.stdout
    passed = "Failed: 0" in stdout
    bytes_val = _extract_bytes(stdout)

    return Attempt(
        version="pending",  # caller fills in
        parent=None,
        code=code,
        bytes=bytes_val,
        passed=passed,
        test_results={
            "stdout": stdout[:3000],
            "stderr": result.stderr[:1000] if result.stderr else "",
            "returncode": result.returncode,
        },
    )


def _extract_bytes(output: str) -> int:
    """Extract code length from verify.py output: 'Code length: 2525 chars'."""
    for line in output.split("\n"):
        if "code length:" in line.lower():
            try:
                return int(line.split(":")[1].strip().split()[0])
            except (IndexError, ValueError):
                pass
    return 0


# ╔══════════════════════════════════════════════════════════════╗
# ║  6. MAIN ORCHESTRATOR                                       ║
# ╚══════════════════════════════════════════════════════════════╝

class GolfSession:
    """
    The main session object. Created once per task directory.
    Persists all state to disk so the LLM can resume after context loss.
    """
    def __init__(self, task_dir: str = "."):
        self.task_dir = os.path.abspath(task_dir)
        self.guard = StateGuard()
        self.knowledge = TaskKnowledge()
        self.dag = VersionDAG(os.path.join(task_dir, "workdir", "dag.json"))
        self._load_session()

    def _load_session(self):
        """Restore session state from disk."""
        session_path = os.path.join(self.task_dir, "workdir", "session.json")
        if os.path.exists(session_path):
            with open(session_path) as f:
                data = json.load(f)
                self.guard.current_state = GolfState(data.get("state", "init"))

        knowledge_path = os.path.join(self.task_dir, "workdir", "knowledge.json")
        if os.path.exists(knowledge_path):
            with open(knowledge_path) as f:
                data = json.load(f)
                if data.get("input_spec"):
                    self.knowledge.input_spec = GridSpec(**data["input_spec"])
                    self.knowledge.input_spec.colors_present = set(
                        self.knowledge.input_spec.colors_present)
                if data.get("output_spec"):
                    self.knowledge.output_spec = GridSpec(**data["output_spec"])
                    self.knowledge.output_spec.colors_present = set(
                        self.knowledge.output_spec.colors_present)
                    self.knowledge.output_spec.colors_output = set(
                        self.knowledge.output_spec.colors_output)
                self.knowledge.transformation_type = data.get("transformation_type", "")
                self.knowledge.transformation_params = data.get("transformation_params", {})
                self.knowledge.invariants = data.get("invariants", [])
                self.knowledge.rules = data.get("rules", [])
                self.knowledge.edge_cases = data.get("edge_cases", [])
                self.knowledge.confidence = data.get("confidence", 0.0)

    def save_session(self):
        """Persist all session state."""
        os.makedirs(os.path.join(self.task_dir, "workdir"), exist_ok=True)

        # State machine
        with open(os.path.join(self.task_dir, "workdir", "session.json"), "w") as f:
            json.dump({"state": self.guard.current_state.value}, f)

        # Knowledge
        k = self.knowledge
        with open(os.path.join(self.task_dir, "workdir", "knowledge.json"), "w") as f:
            json.dump({
                "input_spec": asdict(k.input_spec) if k.input_spec else None,
                "output_spec": asdict(k.output_spec) if k.output_spec else None,
                "transformation_type": k.transformation_type,
                "transformation_params": k.transformation_params,
                "invariants": k.invariants,
                "rules": k.rules,
                "edge_cases": k.edge_cases,
                "confidence": k.confidence,
            }, f, indent=2)

        # DAG (saved separately on each add)
        self.dag.save()

    def submit(self, code: str, parent_version: str, insight: str) -> Attempt:
        """
        The ONE way to submit an attempt. Enforces state, verifies, logs to DAG.
        Returns the Attempt (node in DAG).
        """
        # Can only submit from WRITE_CODE or GOLF
        if self.guard.current_state not in (GolfState.WRITE_CODE, GolfState.GOLF):
            allowed = self.guard.allowed_actions()
            raise AssertionError(
                f"当前状态 {self.guard.current_state.value} 不允许提交代码。"
                f"允许的操作: {allowed}"
            )

        # Generate version
        version = self.dag.next_version(parent_version)

        # Verify
        attempt = verify(code, self.task_dir)
        attempt.version = version
        attempt.parent = parent_version
        attempt.insight = insight

        # If parent exists, compute savings
        parent_node = self.dag.get(parent_version)
        if parent_node:
            attempt.expected_saving = parent_node.bytes - attempt.bytes

        # Add to DAG (auto-saves)
        self.dag.add(attempt)

        # Update state (direct set, submit is an atomic composite action)
        if attempt.passed and attempt.bytes < 100:
            self.guard.current_state = GolfState.DONE
        elif attempt.passed:
            self.guard.current_state = GolfState.GOLF
        else:
            self.guard.current_state = GolfState.WRITE_CODE

        self.save_session()
        return attempt

    def update_knowledge(self, **kwargs):
        """Update structured knowledge fields."""
        for key, value in kwargs.items():
            if hasattr(self.knowledge, key):
                setattr(self.knowledge, key, value)
        self.save_session()

    # ── Status Report (what the LLM should read on startup) ──
    def status_report(self) -> str:
        """Generate a concise status report for the LLM to orient itself."""
        lines = [
            "=" * 60,
            "  COGNITIVE MAP STATUS",
            "=" * 60,
            f"  State:     {self.guard.current_state.value}",
            f"  Allowed:   {self.guard.allowed_actions()}",
            f"  Attempts:  {self.dag.stats()['total_attempts']} total, "
            f"{self.dag.stats()['passing_attempts']} passing",
        ]
        best = self.dag.best()
        if best:
            lines.append(f"  Best:      {best.version} — {best.bytes} bytes")
        lines.append(f"  Knowledge confidence: {self.knowledge.confidence:.0%}")
        lines.append(f"  Rules discovered: {len(self.knowledge.rules)}")
        lines.append("")
        lines.append("  Version Tree:")
        lines.append(self.dag.ascii_tree() or "  (empty)")
        lines.append("=" * 60)
        return "\n".join(lines)


# ╔══════════════════════════════════════════════════════════════╗
# ║  7. QUICK API (what the LLM actually calls)                 ║
# ╚══════════════════════════════════════════════════════════════╝

# Singleton session — created once, persisted to disk
_session: Optional[GolfSession] = None


def get_session(task_dir: str = ".") -> GolfSession:
    """Get or create the singleton GolfSession."""
    global _session
    if _session is None:
        _session = GolfSession(task_dir)
    return _session


def status() -> str:
    """Quick status — call this first on every conversation start."""
    return get_session().status_report()


def submit(code: str, parent: str, insight: str = "") -> Attempt:
    """Submit a candidate. The ONLY way to record an attempt."""
    return get_session().submit(code, parent, insight)


def learn(**kwargs) -> None:
    """Record structured knowledge. Keys must match TaskKnowledge fields."""
    get_session().update_knowledge(**kwargs)


def best() -> Optional[Attempt]:
    """Get the best (shortest passing) attempt so far."""
    return get_session().dag.best()


def tree() -> str:
    """Show the version tree."""
    return get_session().dag.ascii_tree()


def trend() -> List[Tuple[str, int]]:
    """Get the optimization trend for the best chain."""
    return get_session().dag.trend()


# ── Module-level self-test ──
if __name__ == "__main__":
    sess = get_session()
    print(sess.status_report())
    print("\nQuick API available: status(), submit(code, parent, insight), learn(**kw), best(), tree(), trend()")
