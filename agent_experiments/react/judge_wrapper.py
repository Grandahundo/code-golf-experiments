#!/usr/bin/env python3
"""Judge wrapper — runs inside a subprocess for sandbox isolation.

Usage: python judge_wrapper.py <code_path> <cases_path> <per_case_timeout>

Reads test cases from cases_path (JSON), loads user code from code_path,
runs p(input) for each case with per-case timeout, writes JSON-lines results
to stdout (one per case, plus a final summary line).

Exit code 0 = all cases ran (may still be wrong).
Exit code 1 = wrapper itself crashed.
Exit code 2 = import/load failure.
"""

import importlib.util
import json
import os
import signal
import sys
import traceback


# ── Normalize (from official code_golf_utils.py semantics) ──────────

def normalize_output(raw) -> list:
    """Normalize p() output to nested lists of ints.

    Mimics the official Kaggle verifier:
      1. json.dumps the result
      2. Replace true→1, false→0
      3. Validate only safe characters (digits, commas, brackets, whitespace, dots)
      4. json.loads back → purely int lists

    Returns the normalized nested list on success.
    Raises ValueError if output contains unsafe types (str, dict, None, etc.)
    """
    import re

    text = json.dumps(raw)
    text = text.replace("true", "1").replace("false", "0")

    # Validate: only 0-9, comma, bracket, whitespace, dot/minus (for floats)
    unsafe = re.compile(r"[^0-9,\[\]\s\.\-]")
    if unsafe.search(text):
        snippet = text[:500]
        raise ValueError(f"Unsafe characters in output: {snippet}")

    try:
        result = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON decode failed after normalization: {e}")

    return result


def normalize_recursive(obj):
    """Final pass: ensure all values are ints, reject non-int floats and other types.

    After json.dumps→replace→loads, bools are already 1/0 ints.
    Floats like 3.0 need to become 3; non-integral floats (3.5) are rejected.
    """
    if isinstance(obj, list):
        return [normalize_recursive(x) for x in obj]
    elif isinstance(obj, bool):
        return int(obj)
    elif isinstance(obj, float):
        if obj == int(obj):
            return int(obj)
        raise ValueError(f"Non-integral float in output: {obj}")
    elif isinstance(obj, int):
        return obj
    elif isinstance(obj, tuple):
        return [normalize_recursive(x) for x in obj]
    else:
        raise ValueError(f"Unsupported type in output: {type(obj).__name__} = {str(obj)[:200]}")


def arrays_equal(a, b) -> bool:
    """Compare two normalized nested lists — numpy.array_equal semantics."""
    return a == b


# ── Main ────────────────────────────────────────────────────────────

def load_code(code_path: str):
    """Import user module and return the callable p."""
    spec = importlib.util.spec_from_file_location("candidate", code_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "p"):
        raise AttributeError(f"No callable 'p' defined in {code_path}")
    p = getattr(mod, "p")
    if not callable(p):
        raise TypeError(f"'p' in {code_path} is not callable")
    return p


class TimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutError("per-case timeout")


def run_one_case(p, test_case: dict, timeout_s: float, index: int) -> dict:
    """Run p on a single test case with timeout. Returns a result dict."""
    inp = test_case["input"]
    expected_raw = test_case["output"]

    # Normalize expected once upfront
    try:
        expected = normalize_output(expected_raw)
        expected = normalize_recursive(expected)
    except ValueError as e:
        return {
            "index": index,
            "status": "judge_error",
            "error": f"Failed to normalize expected output: {e}",
        }

    # Set per-case alarm
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(int(timeout_s) + 1)  # alarm takes int seconds, +1 for safety

    try:
        raw = p(inp)
        signal.alarm(0)  # cancel alarm

        # Normalize
        normalized = normalize_output(raw)
        normalized = normalize_recursive(normalized)

        if arrays_equal(normalized, expected):
            return {"index": index, "status": "pass"}
        else:
            return {
                "index": index,
                "status": "fail",
                "input": inp,
                "expected": expected_raw,
                "actual": raw,
            }

    except TimeoutError:
        return {"index": index, "status": "timeout"}
    except Exception as e:
        signal.alarm(0)
        return {
            "index": index,
            "status": "error",
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc()[-500:],
        }


def main():
    if len(sys.argv) != 4:
        print("Usage: judge_wrapper.py <code_path> <cases_path> <per_case_timeout>",
              file=sys.stderr)
        sys.exit(1)

    code_path = sys.argv[1]
    cases_path = sys.argv[2]
    per_case_timeout = float(sys.argv[3])

    # ── Load test cases ─────────────────────────────────────────
    with open(cases_path) as f:
        cases = json.load(f)

    # ── Set resource limits (before importing user code) ─────────
    try:
        import resource
        # AS = 512 MB
        as_limit = 512 * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (as_limit, as_limit))
        # NPROC = 32
        resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))
        # FSIZE = 8 MB
        resource.setrlimit(resource.RLIMIT_FSIZE, (8 * 1024 * 1024, 8 * 1024 * 1024))
    except (ImportError, ValueError, resource.error):
        # macOS: RLIMIT_AS is advisory, RLIMIT_NPROC may not exist
        pass

    # ── Load user code (with 5s alarm) ───────────────────────────
    signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(5)

    try:
        p = load_code(code_path)
        signal.alarm(0)
    except TimeoutError:
        print(json.dumps({"stage": "import_timeout"}))
        sys.exit(2)
    except Exception as e:
        print(json.dumps({
            "stage": "import_error",
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc()[-500:],
        }))
        sys.exit(2)

    # ── Run test cases ───────────────────────────────────────────
    results = []
    failed_count = 0
    short_circuit = False

    for i, case in enumerate(cases):
        if short_circuit:
            results.append({"index": i, "status": "not_run"})
            continue

        result = run_one_case(p, case, per_case_timeout, i)
        results.append(result)

        if result["status"] not in ("pass",):
            failed_count += 1

        # Short-circuit: stop after 3 failures
        if failed_count >= 3:
            short_circuit = True

        # Write result line immediately
        print(json.dumps(result), flush=True)

    # Summary line (distinguished by special key)
    summary = {
        "_summary": True,
        "total": len(cases),
        "ran": len([r for r in results if r["status"] != "not_run"]),
        "passed": len([r for r in results if r["status"] == "pass"]),
        "short_circuit": short_circuit,
    }
    print(json.dumps(summary), flush=True)

    all_pass = summary["passed"] == summary["total"]
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
