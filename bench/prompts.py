"""Prompt templates for the code golf agentic loop.

All templates are centralized here per spec-v2 §3.2.
"""

# ── System prompt (fixed, serves as cache prefix) ────────────────────

SYSTEM_PROMPT = """You are a code golf expert. Your task is to write the shortest possible Python program that defines a callable `p(grid) -> grid` solving the given problem.

## Rules
- `p` receives a nested list of ints (the input grid) and must return a nested list of ints (the output grid).
- All cell values are integers between 0 and 9.
- Your score = the UTF-8 byte count of your final file (shorter is better).
- You must define `p` as either a function (`def p(g):`) or lambda (`p=lambda g:...`).
- Standard library only. No third-party imports (no numpy, scipy, etc.).
- The judge uses numpy.array_equal semantics: booleans and integral floats are auto-converted to ints.

## Strategy
1. **Study the generator code** (if provided below) — it IS the ground truth for the transformation rule.
2. **First get a correct solution**, then compress iteratively.
3. Apply ONE optimization at a time, verify after each change.
4. Explore multiple approaches in parallel when stuck.

## Output Format
You must respond with:
1. `<notes>...</notes>` — your scratchpad (≤500 tokens): record your understanding of the rule, what you tried, why it failed, and your next plan.
2. A ````python` code block containing your complete program — put this LAST in your response.

Only the last Python code block in your reply will be judged."""


# ── User message sections ────────────────────────────────────────────

def build_user_prompt(
    task_id: str,
    gen_source: str,
    has_gen: bool,
    train_examples: list,       # list of (display_input, display_output) strs
    round_no: int,
    max_rounds: int,
    best_bytes: "int | None",
    best_code: "str | None",
    scratchpad: str,
    history_entries: list[str],  # pre-formatted history strings
) -> str:
    """Build the user message for one round of the agentic loop.

    Sections: [B] gen.py, [C] train examples, [D] current state,
              [E] scratchpad, [F] recent history, [G] output format.
    """
    parts = []

    # [B] Generator source
    if has_gen and gen_source:
        parts.append(f"## Generator Code (ground truth)\n\n```python\n{gen_source}\n```")
    else:
        parts.append(
            "## Generator Code\n\n"
            "No generator source is available for this task. "
            "You must infer the transformation rule entirely from the training examples below."
        )

    # [C] Train examples
    parts.append("## Training Examples")
    if not train_examples:
        parts.append("(No training examples available.)")
    else:
        for i, (inp_disp, out_disp) in enumerate(train_examples, 1):
            parts.append(f"### Example {i}\nInput:\n{inp_disp}\n\nOutput:\n{out_disp}")

    # [D] Current state
    parts.append("## Current Status")
    parts.append(f"Round {round_no}/{max_rounds}")
    if best_bytes is not None and best_code is not None:
        parts.append(f"Best so far: {best_bytes} bytes (correct)")
        parts.append(f"```python\n{best_code}\n```")
    else:
        parts.append("Best so far: NO CORRECT SOLUTION YET — prioritize getting one that passes all tests.")

    # [E] Scratchpad (model's own notes from previous round)
    parts.append("## Your Notes (from last round)")
    if scratchpad:
        parts.append(scratchpad)
    else:
        parts.append("(First round — no notes yet.)")

    # [F] Recent history
    parts.append("## Recent Attempts")
    if history_entries:
        parts.extend(history_entries)
    else:
        parts.append("(No attempts yet.)")

    # [G] Output format reminder
    parts.append(
        "## Instructions\n\n"
        "Update your notes in `<notes>...</notes>` (≤500 tokens: record what you've learned "
        "about the transformation rule, what approaches you've tried, why they failed, "
        "and what you plan to try next). "
        "Then write your complete Python program in a ```python code block at the END of your reply. "
        "Only the LAST Python code block is judged."
    )

    return "\n\n".join(parts)


# ── Feedback formatters (§2.3 taxonomy) ──────────────────────────────

def format_parse_error() -> str:
    return ("**Feedback:** Could not extract a Python code block from your reply. "
            "Make sure your response ends with a ```python code block.")


def format_syntax_error(error: str) -> str:
    return f"**Feedback:** Your code has a syntax error and could not run:\n```\n{error}\n```"


def format_no_p(error: str) -> str:
    return (f"**Feedback:** Your code does not define a callable `p`:\n```\n{error}\n```\n"
            "Make sure your code defines `p` as a function or lambda.")


def format_crash(error: str) -> str:
    return f"**Feedback:** Your code crashed during execution:\n```\n{error}\n```"


def format_wrong(passed: int, ran: int, total: int,
                 failures: list[dict]) -> str:
    """Format wrong-answer feedback with failure examples."""
    lines = [f"**Feedback:** Your code ran but gave wrong outputs."]
    lines.append(f"Passed {passed}/{ran} (of {total} total test cases).")

    if failures:
        lines.append(f"\nFailures (showing up to {len(failures)}):")
        for i, f in enumerate(failures, 1):
            lines.append(f"\n  Failure {i} — status: {f.get('status', '?')}")
            if "input" in f:
                lines.append(f"  Input:\n    {_indent(str(f['input']), 4)}")
            if "expected" in f:
                lines.append(f"  Expected:\n    {_indent(str(f['expected']), 4)}")
            if "actual" in f:
                lines.append(f"  Actual:\n    {_indent(str(f['actual']), 4)}")
            if "error" in f:
                lines.append(f"  Error: {f['error']}")

    return "\n".join(lines)


def format_correct(byte_count: int, is_record: bool = False) -> str:
    """Format correct-answer feedback."""
    record_note = " **NEW RECORD!**" if is_record else ""
    return f"**Feedback:** ✓ Correct! Your solution is {byte_count} bytes.{record_note}"


def format_timeout(error: str) -> str:
    return f"**Feedback:** Your code timed out:\n```\n{error}\n```"


def _indent(text: str, spaces: int) -> str:
    """Indent each line of text by spaces."""
    prefix = " " * spaces
    return "\n".join(prefix + line for line in text.splitlines())


# ── History entry builder ────────────────────────────────────────────

def build_history_entry(
    round_no: int,
    code: str,
    byte_count: int,
    status: str,
    feedback_str: str,
    max_code_chars: int = 2000,
) -> str:
    """Build a single history entry for injection into the prompt."""
    code_display = code
    if len(code) > max_code_chars:
        mid = max_code_chars // 2
        code_display = (
            code[:mid]
            + f"\n# ... (truncated, {len(code) - max_code_chars} chars omitted)\n"
            + code[-mid:]
        )

    return (
        f"### Round {round_no} (previous)\n"
        f"Bytes: {byte_count} | Status: {status}\n"
        f"```python\n{code_display}\n```\n"
        f"{feedback_str}"
    )
