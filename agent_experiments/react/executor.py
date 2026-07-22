"""Sandbox executor — runs user code via judge_wrapper subprocess with resource limits.

Architecture per spec-v2 §2.1:
  Single subprocess per judgment → wrapper loads code → runs all cases with
  per-case alarm → streams JSON-lines results back.
"""

import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Optional

from task_loader import TaskBundle


@dataclass
class JudgeResult:
    """Result of judging one submission against all hidden test cases."""
    status: str             # correct | wrong | crash | syntax_error | no_p | timeout
    passed: int = 0
    total: int = 0
    ran: int = 0
    byte_count: int = 0
    kaggle_score: int = 0
    failures: list[dict] = field(default_factory=list)
    error: str = ""         # crash message / traceback if applicable
    elapsed_s: float = 0.0


# ── Public API ───────────────────────────────────────────────────────

def judge(code: str, bundle: TaskBundle, *,
          python_bin: str = "python3",
          per_case_timeout: float = 2.0,
          padding_s: float = 10.0,
          max_timeout: float = 120.0,
          max_failures_shown: int = 3,
          max_failure_chars: int = 500,
          short_circuit_failures: int = 3,
          ) -> JudgeResult:
    """Judge one solution against a task's hidden test cases.

    Args:
        code: the full Python source code defining p(grid)->grid
        bundle: TaskBundle with hidden test cases
        per_case_timeout: seconds per test case (alarm in wrapper)
        padding_s: added to total timeout
        max_timeout: hard cap on subprocess timeout
        max_failures_shown: max failure entries in result
        max_failure_chars: truncate failure fields to this length
        short_circuit_failures: stop after this many failures

    Returns:
        JudgeResult with full judgment details.
    """
    t0 = time.time()

    # ── Syntax check (fast path, no subprocess) ───────────────────
    try:
        compile(code, "<solution>", "exec")
    except SyntaxError as e:
        return JudgeResult(
            status="syntax_error",
            total=len(bundle.hidden),
            error=f"SyntaxError: {e.msg} (line {e.lineno})",
            elapsed_s=time.time() - t0,
        )

    # ── Compute byte count ────────────────────────────────────────
    stripped = code.strip()
    byte_count = len(stripped.encode("utf-8"))
    kaggle_score = max(1, 2500 - byte_count)

    # ── Write code to temp file ───────────────────────────────────
    wrapper_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "judge_wrapper.py")

    with tempfile.TemporaryDirectory(prefix="golf_judge_") as tmpdir:
        code_path = os.path.join(tmpdir, "solution.py")
        cases_path = os.path.join(tmpdir, "cases.json")

        with open(code_path, "w") as f:
            f.write(stripped)

        # Serialize hidden cases
        cases = [{"input": ex.input, "output": ex.output} for ex in bundle.hidden]
        with open(cases_path, "w") as f:
            json.dump(cases, f)

        n_cases = len(cases)
        total_timeout = min(padding_s + per_case_timeout * n_cases, max_timeout)

        # ── Run subprocess ────────────────────────────────────────
        try:
            proc = subprocess.run(
                [python_bin, wrapper_path, code_path, cases_path, str(per_case_timeout)],
                capture_output=True, text=True,
                timeout=total_timeout,
                start_new_session=True,
            )
        except subprocess.TimeoutExpired:
            return JudgeResult(
                status="timeout",
                total=n_cases,
                byte_count=byte_count,
                kaggle_score=kaggle_score,
                error=f"Overall timeout after {total_timeout:.0f}s",
                elapsed_s=time.time() - t0,
            )

    elapsed = time.time() - t0

    # ── Parse output ──────────────────────────────────────────────
    return _parse_wrapper_output(
        proc, n_cases, byte_count, kaggle_score, elapsed,
        max_failures_shown, max_failure_chars,
    )


# ── Internal ─────────────────────────────────────────────────────────

def _parse_wrapper_output(
    proc: subprocess.CompletedProcess,
    total_cases: int,
    byte_count: int,
    kaggle_score: int,
    elapsed: float,
    max_failures_shown: int,
    max_failure_chars: int,
) -> JudgeResult:
    """Parse wrapper stdout/stderr into a JudgeResult."""

    stdout = proc.stdout or ""
    stderr = proc.stderr or ""

    # Check for import-level failures (wrapper writes stage info as first JSON line)
    lines = [l.strip() for l in stdout.splitlines() if l.strip()]

    if not lines:
        return JudgeResult(
            status="crash",
            total=total_cases,
            byte_count=byte_count,
            kaggle_score=kaggle_score,
            error=f"No output from wrapper. stderr: {stderr[-500:]}",
            elapsed_s=elapsed,
        )

    # Check first line for stage errors
    try:
        first = json.loads(lines[0])
    except json.JSONDecodeError:
        return JudgeResult(
            status="crash",
            total=total_cases,
            byte_count=byte_count,
            kaggle_score=kaggle_score,
            error=f"Wrapper malformed output: {stdout[:500]}",
            elapsed_s=elapsed,
        )

    if isinstance(first, dict):
        stage = first.get("stage", "")
        if stage == "import_timeout":
            return JudgeResult(
                status="crash",
                total=total_cases,
                byte_count=byte_count,
                kaggle_score=kaggle_score,
                error="Import timed out (5s limit)",
                elapsed_s=elapsed,
            )
        elif stage == "import_error":
            err = first.get("error", "")
            tb = first.get("traceback", "")
            # Classify: no 'p' attribute vs other import errors
            if "No callable 'p'" in err or "not callable" in err:
                return JudgeResult(
                    status="no_p",
                    total=total_cases,
                    byte_count=byte_count,
                    kaggle_score=kaggle_score,
                    error=err,
                    elapsed_s=elapsed,
                )
            return JudgeResult(
                status="crash",
                total=total_cases,
                byte_count=byte_count,
                kaggle_score=kaggle_score,
                error=f"{err}\n{tb}" if tb else err,
                elapsed_s=elapsed,
            )

    # Parse case results and summary
    case_results = []
    summary = None
    for line in lines:
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("_summary"):
            summary = obj
        elif isinstance(obj, dict) and "_summary" not in obj:
            case_results.append(obj)

    if summary is None:
        # Wrapper crashed before writing summary — try to use partial results
        passed = sum(1 for r in case_results if r["status"] == "pass")
        ran = len(case_results)
        return JudgeResult(
            status="crash",
            passed=passed, total=total_cases, ran=ran,
            byte_count=byte_count, kaggle_score=kaggle_score,
            error=f"Wrapper crashed. stderr: {stderr[-500:]}" if stderr else "Wrapper crashed",
            failures=_build_failures(case_results, max_failures_shown, max_failure_chars),
            elapsed_s=elapsed,
        )

    passed = summary["passed"]
    ran = summary["ran"]
    all_pass = passed == total_cases

    # Determine the overall status from case-level results
    case_statuses = {r.get("status") for r in case_results}
    num_error = sum(1 for r in case_results if r["status"] == "error")
    num_timeout = sum(1 for r in case_results if r["status"] == "timeout")
    num_fail = sum(1 for r in case_results if r["status"] == "fail")

    if all_pass:
        status = "correct"
    elif num_timeout > 0 and num_fail == 0 and num_error == 0:
        status = "timeout"
    elif num_error > 0 or num_timeout > 0:
        # Mix of errors/timeouts and possibly wrong answers → crash
        status = "crash"
    else:
        status = "wrong"

    # Build aggregate error message for crash/timeout cases
    error_parts = []
    if num_error > 0:
        err_msgs = [r.get("error", "") for r in case_results if r["status"] == "error"]
        error_parts.append(f"{num_error} case(s) crashed: {'; '.join(err_msgs[:3])}")
    if num_timeout > 0:
        error_parts.append(f"{num_timeout} case(s) timed out")
    error = "; ".join(error_parts) if error_parts else ""

    return JudgeResult(
        status=status,
        passed=passed, total=total_cases, ran=ran,
        byte_count=byte_count, kaggle_score=kaggle_score,
        failures=_build_failures(case_results, max_failures_shown, max_failure_chars),
        error=error,
        elapsed_s=elapsed,
    )


def _build_failures(results: list[dict], max_count: int, max_chars: int) -> list[dict]:
    """Build trimmed failure list, preferring shortest inputs."""
    failures = [r for r in results if r.get("status") not in ("pass", "not_run")]
    # Sort by input size (helpful for model feedback)
    failures.sort(key=lambda r: len(json.dumps(r.get("input", []))))

    trimmed = []
    for f in failures[:max_count]:
        entry = {"status": f["status"]}
        for key in ("input", "expected", "actual", "error"):
            if key in f:
                val = f[key]
                if isinstance(val, (list, dict)):
                    val = json.dumps(val)
                val = str(val)
                if len(val) > max_chars:
                    val = val[:max_chars] + f"... (truncated, full: {len(val)} chars)"
                entry[key] = val
        trimmed.append(entry)
    return trimmed
