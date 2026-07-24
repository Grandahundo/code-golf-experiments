#!/usr/bin/env python3
"""Test a candidate solution against a task's train+test examples.

Runs in its own process so that crashes / infinite loops in generated code
can be contained by the parent's subprocess timeout.

Usage: python3 harness.py <solution.py> <task.json>
Prints one JSON object to stdout:
  {"passed": int, "total": int, "correct": bool, "error": str|null, "failures": [...]}
"""

import importlib.util
import json
import sys


def normalize(grid):
    """Coerce a grid-like value to nested lists of ints.

    Mirrors the official check (numpy.array_equal): tuples, booleans and
    floats with integral values are accepted as long as values align.
    """
    return [[int(c) for c in row] for row in grid]


def main():
    sol_path, json_path = sys.argv[1], sys.argv[2]
    with open(json_path) as f:
        data = json.load(f)

    result = {"passed": 0, "total": 0, "correct": False, "error": None, "failures": []}

    try:
        spec = importlib.util.spec_from_file_location("candidate", sol_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        p = getattr(mod, "p")
    except Exception as e:
        result["error"] = f"load: {e!r}"
        result["total"] = sum(len(data[s]) for s in ("train", "test"))
        print(json.dumps(result))
        return

    for split in ("train", "test"):
        for i, ex in enumerate(data[split]):
            result["total"] += 1
            try:
                got = normalize(p(ex["input"]))
            except Exception as e:
                result["failures"].append(f"{split}[{i}]: {e!r}")
                continue
            if got == ex["output"]:
                result["passed"] += 1
            else:
                result["failures"].append(f"{split}[{i}]: wrong output")

    result["correct"] = result["total"] > 0 and result["passed"] == result["total"]
    print(json.dumps(result))


if __name__ == "__main__":
    main()
