"""Agentic loop — single (task, model, seed) job.

Architecture per spec-v2 §3:
  Near-stateless: each round rebuilds the full prompt from scratchpad + history.
  Everything is persisted to disk for resume.
"""

import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Union

from task_loader import TaskBundle, select_train_examples, grid_to_display
from executor import judge, JudgeResult
from llm import LLMClient, Usage
from prompts import (
    SYSTEM_PROMPT,
    build_user_prompt,
    build_history_entry,
    format_parse_error,
    format_syntax_error,
    format_no_p,
    format_crash,
    format_wrong,
    format_correct,
    format_timeout,
)


@dataclass
class RoundRecord:
    round_no: int
    ts: str
    code: str
    byte_count: int
    kaggle_score: int
    status: str            # §2.3 taxonomy
    passed: int
    ran: int
    total: int
    failures_shown: list[dict]
    scratchpad: str
    usage: "Usage | dict"
    error: str = ""


@dataclass
class JobState:
    task_id: str
    model: str
    seed: int
    round_no: int = 0
    best_code: Optional[str] = None
    best_bytes: Optional[int] = None
    best_kaggle: int = 0
    scratchpad: str = ""
    history: list[RoundRecord] = field(default_factory=list)
    tokens_used: int = 0
    first_correct_round: Optional[int] = None
    bytes_curve: "list[Optional[int]]" = field(default_factory=list)
    consecutive_api_errors: int = 0
    finished: bool = False


def parse_reply(text: str, prev_scratchpad: str) -> "tuple[Optional[str], str]":
    """Extract code and scratchpad from model reply.

    Returns (code, scratchpad). code is None on parse_error.
    """
    # Extract notes
    notes_match = re.search(r"<notes>(.*?)</notes>", text, re.DOTALL | re.IGNORECASE)
    scratchpad = notes_match.group(1).strip() if notes_match else prev_scratchpad

    # Truncate scratchpad
    if len(scratchpad) > 3000:
        scratchpad = scratchpad[:3000]

    # Extract last python code block
    code_blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if not code_blocks:
        return None, scratchpad

    code = code_blocks[-1].strip()
    if not code:
        return None, scratchpad

    return code, scratchpad


def feedback_text(result: JudgeResult, is_record: bool = False) -> str:
    """Build feedback string for a judged round."""
    status = result.status
    if status == "parse_error":
        return format_parse_error()
    elif status == "syntax_error":
        return format_syntax_error(result.error)
    elif status == "no_p":
        return format_no_p(result.error)
    elif status == "crash":
        return format_crash(result.error)
    elif status == "timeout":
        return format_timeout(result.error)
    elif status == "wrong":
        return format_wrong(result.passed, result.ran, result.total, result.failures)
    elif status == "correct":
        return format_correct(result.byte_count, is_record)
    return f"Unknown status: {status}"


async def run_job(
    bundle: TaskBundle,
    model_key: str,
    llm: LLMClient,
    seed: int,
    config: dict,
    output_dir: str,
) -> JobState:
    """Run the full agentic loop for one (task, model, seed) job.

    Args:
        bundle: loaded TaskBundle
        model_key: key into config.models
        llm: LLMClient instance
        seed: random seed for reproducibility
        config: full config dict
        output_dir: path like runs/{model}/{task_id}/seed{n}/

    Returns:
        final JobState with all records saved to disk.
    """
    os.makedirs(output_dir, exist_ok=True)

    max_rounds = config.get("max_rounds", 30)
    token_budget = config.get("token_budget_per_job", 1_500_000)
    temperature = config.get("temperature", 0.7)
    history_window = config.get("history_window", 3)
    early_stop = config.get("early_stop", {}).get("no_improve_rounds")

    state = _restore_or_init(output_dir, bundle.task_id, model_key, seed)

    # ── Pre-select train examples (stable across all rounds) ────────
    selected_train = select_train_examples(
        bundle,
        max_count=config.get("train_examples_max", 3),
        max_chars=config.get("train_example_max_chars", 1500),
    )
    train_displays = [
        (grid_to_display(ex.input), grid_to_display(ex.output))
        for ex in selected_train
    ]

    no_improve_count = 0

    while state.round_no < max_rounds and state.tokens_used < token_budget:
        round_no = state.round_no + 1

        # ── Build prompt ───────────────────────────────────────────
        history_entries = []
        for rec in state.history[-history_window:]:
            fb = feedback_text_from_record(rec)
            history_entries.append(
                build_history_entry(rec.round_no, rec.code, rec.byte_count,
                                    rec.status, fb)
            )

        user_prompt = build_user_prompt(
            task_id=bundle.task_id,
            gen_source=bundle.gen_source,
            has_gen=bundle.has_gen,
            train_examples=train_displays,
            round_no=round_no,
            max_rounds=max_rounds,
            best_bytes=state.best_bytes,
            best_code=state.best_code,
            scratchpad=state.scratchpad,
            history_entries=history_entries,
        )

        # ── Estimate & trim prompt if needed ────────────────────────
        prompt_budget = config.get("prompt_token_budget", 22000)
        est_tokens = (len(SYSTEM_PROMPT) + len(user_prompt)) // 3
        if est_tokens > prompt_budget:
            # Already using history_window, but gen.py might be large
            # Trim gen_source from prompt (rely on train examples)
            user_prompt = _trim_prompt(user_prompt, prompt_budget)

        # ── Call LLM ───────────────────────────────────────────────
        try:
            reply_text, usage = await llm.chat(
                model_key, SYSTEM_PROMPT, user_prompt,
                temperature=temperature, seed=seed,
            )
            state.tokens_used += usage.input_tokens + usage.output_tokens
            state.consecutive_api_errors = 0
        except Exception as e:
            state.consecutive_api_errors += 1
            record = RoundRecord(
                round_no=round_no,
                ts=datetime.now(timezone.utc).isoformat(),
                code="",
                byte_count=0,
                kaggle_score=0,
                status="api_error",
                passed=0, ran=0, total=len(bundle.hidden),
                failures_shown=[],
                scratchpad=state.scratchpad,
                usage={"error": str(e)},
                error=str(e),
            )
            _append_trajectory(output_dir, record)
            if state.consecutive_api_errors >= 10:
                state.finished = False
                _write_meta(output_dir, state)
                return state
            continue

        state.tokens_used += usage.input_tokens + usage.output_tokens

        # ── Parse reply ────────────────────────────────────────────
        code, scratchpad = parse_reply(reply_text, state.scratchpad)

        if code is None:
            # parse_error — counts as a round
            record = RoundRecord(
                round_no=round_no,
                ts=datetime.now(timezone.utc).isoformat(),
                code="",
                byte_count=0,
                kaggle_score=0,
                status="parse_error",
                passed=0, ran=0, total=len(bundle.hidden),
                failures_shown=[],
                scratchpad=scratchpad,
                usage=_usage_to_dict(usage),
            )
            state.round_no = round_no
            state.scratchpad = scratchpad
            state.history.append(record)
            state.bytes_curve.append(state.best_bytes)
            _append_trajectory(output_dir, record)
            continue

        state.scratchpad = scratchpad

        # ── Judge ──────────────────────────────────────────────────
        result = judge(
            code, bundle,
            python_bin=config.get("python_bin", "python3"),
            per_case_timeout=config.get("per_case_timeout", 2.0),
            padding_s=config.get("judge_timeout_padding", 10),
            max_timeout=config.get("judge_max_timeout", 120),
            max_failures_shown=config.get("max_failures_shown", 3),
            max_failure_chars=config.get("max_failure_chars", 500),
            short_circuit_failures=config.get("short_circuit_failures", 3),
        )

        # ── Update best ────────────────────────────────────────────
        is_record = False
        if result.status == "correct":
            if state.best_bytes is None or result.byte_count < state.best_bytes:
                is_record = True
                state.best_bytes = result.byte_count
                state.best_code = code
                state.best_kaggle = result.kaggle_score
                if state.first_correct_round is None:
                    state.first_correct_round = round_no
                # Write best.py
                with open(os.path.join(output_dir, "best.py"), "w") as f:
                    f.write(code.strip())

        # ── Record round ───────────────────────────────────────────
        record = RoundRecord(
            round_no=round_no,
            ts=datetime.now(timezone.utc).isoformat(),
            code=code,
            byte_count=result.byte_count,
            kaggle_score=result.kaggle_score,
            status=result.status,
            passed=result.passed,
            ran=result.ran,
            total=result.total,
            failures_shown=result.failures,
            scratchpad=scratchpad,
            usage=_usage_to_dict(usage),
            error=result.error,
        )
        state.round_no = round_no
        state.history.append(record)
        state.bytes_curve.append(state.best_bytes)
        _append_trajectory(output_dir, record)

        # ── Early stopping check ───────────────────────────────────
        if early_stop:
            if is_record or (state.best_bytes is None and result.status == "correct"):
                no_improve_count = 0
            else:
                no_improve_count += 1
            if no_improve_count >= early_stop:
                break

    state.finished = state.round_no >= max_rounds
    _write_meta(output_dir, state)
    return state


# ── Internal helpers ─────────────────────────────────────────────────

def _restore_or_init(output_dir: str, task_id: str, model: str, seed: int) -> JobState:
    """Restore state from disk or create fresh."""
    meta_path = os.path.join(output_dir, "meta.json")
    if os.path.exists(meta_path):
        with open(meta_path) as f:
            meta = json.load(f)
        if meta.get("finished"):
            # Already complete — return minimal state
            state = JobState(task_id=task_id, model=model, seed=seed)
            state.finished = True
            state.round_no = meta.get("rounds_used", 0)
            state.best_bytes = meta.get("best_bytes")
            state.best_code = meta.get("best_code")
            state.tokens_used = meta.get("total_usage", {}).get("total", 0)
            return state

    # Try to restore from trajectory
    traj_path = os.path.join(output_dir, "trajectory.jsonl")
    state = JobState(task_id=task_id, model=model, seed=seed)

    if os.path.exists(traj_path):
        with open(traj_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec_data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                state.round_no = rec_data.get("round", 0)
                state.scratchpad = rec_data.get("scratchpad", "")
                state.tokens_used += (
                    rec_data.get("usage", {}).get("input", 0)
                    + rec_data.get("usage", {}).get("output", 0)
                )
                if rec_data.get("correct") and rec_data.get("byte_count"):
                    bc = rec_data["byte_count"]
                    if state.best_bytes is None or bc < state.best_bytes:
                        state.best_bytes = bc
                        state.best_code = rec_data.get("code", "")
                        state.best_kaggle = rec_data.get("kaggle_score", 0)
                        if state.first_correct_round is None:
                            state.first_correct_round = rec_data["round"]
                state.bytes_curve.append(state.best_bytes)
                # Reconstruct history (last N entries sufficient)
                state.history.append(RoundRecord(
                    round_no=rec_data.get("round", 0),
                    ts=rec_data.get("ts", ""),
                    code=rec_data.get("code", ""),
                    byte_count=rec_data.get("byte_count", 0),
                    kaggle_score=rec_data.get("kaggle_score", 0),
                    status=rec_data.get("status", "?"),
                    passed=rec_data.get("passed", 0),
                    ran=rec_data.get("ran", 0),
                    total=rec_data.get("total", 0),
                    failures_shown=rec_data.get("failures_shown", []),
                    scratchpad=rec_data.get("scratchpad", ""),
                    usage=rec_data.get("usage", {}),
                    error=rec_data.get("error", ""),
                ))

    # Also restore best.py if it exists
    best_path = os.path.join(output_dir, "best.py")
    if os.path.exists(best_path) and state.best_code is None:
        with open(best_path) as f:
            state.best_code = f.read()
            state.best_bytes = len(state.best_code.strip().encode("utf-8"))

    return state


def _append_trajectory(output_dir: str, record: RoundRecord):
    """Append one round to trajectory.jsonl."""
    traj_path = os.path.join(output_dir, "trajectory.jsonl")
    d = {
        "round": record.round_no,
        "ts": record.ts,
        "code": record.code,
        "byte_count": record.byte_count,
        "kaggle_score": record.kaggle_score,
        "correct": record.status == "correct",
        "passed": record.passed,
        "ran": record.ran,
        "total": record.total,
        "failures_shown": record.failures_shown,
        "scratchpad": record.scratchpad,
        "usage": record.usage if isinstance(record.usage, dict) else _usage_to_dict(record.usage),
        "status": record.status,
        "error": record.error,
    }
    with open(traj_path, "a") as f:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")


def _write_meta(output_dir: str, state: JobState):
    """Write meta.json with job summary."""
    import platform

    total_input = 0
    total_output = 0
    total_cached = 0

    # Count from trajectory for accurate totals
    traj_path = os.path.join(output_dir, "trajectory.jsonl")
    if os.path.exists(traj_path):
        with open(traj_path) as f:
            for line in f:
                try:
                    u = json.loads(line.strip()).get("usage", {})
                    total_input += u.get("input", 0)
                    total_output += u.get("output", 0)
                    total_cached += u.get("cached", 0)
                except (json.JSONDecodeError, KeyError):
                    pass

    meta = {
        "task_id": state.task_id,
        "model": state.model,
        "seed": state.seed,
        "finished": state.finished,
        "rounds_used": state.round_no,
        "first_correct_round": state.first_correct_round,
        "best_bytes": state.best_bytes,
        "best_kaggle_score": state.best_kaggle,
        "best_code": state.best_code,
        "bytes_curve": state.bytes_curve,
        "total_usage": {
            "input": total_input,
            "output": total_output,
            "cached": total_cached,
            "total": total_input + total_output,
        },
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "early_stop_config": None,  # filled by runner
    }
    with open(os.path.join(output_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)


def _usage_to_dict(u: "Usage | dict") -> dict:
    if isinstance(u, dict):
        return u
    return {
        "input": u.input_tokens,
        "output": u.output_tokens,
        "cached": u.cached_input_tokens,
    }


def feedback_text_from_record(rec: RoundRecord) -> str:
    """Reconstruct feedback text from a stored round record."""
    status = rec.status
    if status == "parse_error":
        return format_parse_error()
    elif status == "syntax_error":
        return format_syntax_error(rec.error)
    elif status == "no_p":
        return format_no_p(rec.error)
    elif status == "crash":
        return format_crash(rec.error)
    elif status == "timeout":
        return format_timeout(rec.error)
    elif status == "wrong":
        return format_wrong(rec.passed, rec.ran, rec.total, rec.failures_shown)
    elif status == "correct":
        return format_correct(rec.byte_count, False)
    return f"{status}"


def _trim_prompt(user_prompt: str, token_budget: int) -> str:
    """Trim prompt parts to fit token budget (rough heuristic)."""
    # Split on section headers, drop middle of gen.py if needed
    parts = user_prompt.split("\n\n## ")
    # Keep header + last parts (state, notes, history, instructions)
    if len(parts) <= 3:
        # Can't trim much — truncate gen.py block
        return user_prompt[:token_budget * 3]
    # Keep first section (gen.py header) and last 3 sections
    kept = [parts[0]] + parts[-3:]
    result = "\n\n## ".join(kept)
    if len(result) // 3 > token_budget:
        result = result[:token_budget * 3]
    return result
