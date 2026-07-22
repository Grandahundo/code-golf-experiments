#!/usr/bin/env python3
"""30 轮固定循环的 code golf agent —— 单文件，直接跑。

用法:
    python run.py                                    # task001, deepseek, 30 轮
    python run.py --task task003 --model qwen        # 换 qwen
    python run.py --task task005 --rounds 50
"""

import argparse
import json
import os
import re
import time

# ── API 配置 ───────────────────────────────────────────────────────────

QWEN_API_KEY = "sk-ws-H.EHMELMI.6as6.MEUCIQCZ6VtBnH15HJKtuuGDKdi-fulWcTjGxK2T_DbDflbATAIgGMPTGi1tQIe5y2Ez5e8jmj9vxGcYswLB781AjV0XKvw"
QWEN_BASE = "https://ws-ws3qpraz4z2mszz9.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"

API_CONFIGS = {
    "deepseek-v4-pro": {
        "base_url": "https://api.deepseek.com/v1",
        "api_key": "sk-6a2eeea6cc2d4d2596f0b5ae8a023c67",
        "model_name": "deepseek-v4-pro",
        "extra_body": {"thinking": {"type": "enabled"}},
    },
    "deepseek-v4-flash": {
        "base_url": "https://api.deepseek.com/v1",
        "api_key": "sk-6a2eeea6cc2d4d2596f0b5ae8a023c67",
        "model_name": "deepseek-v4-flash",
        "extra_body": {},
    },
    "qwen3.6-flash": {
        "base_url": QWEN_BASE,
        "api_key": QWEN_API_KEY,
        "model_name": "qwen3.6-flash",
        "extra_body": {},
    },
    "qwen3.7-plus": {
        "base_url": QWEN_BASE,
        "api_key": QWEN_API_KEY,
        "model_name": "qwen3.7-plus",
        "extra_body": {},
    },
    "qwen3.7-max": {
        "base_url": QWEN_BASE,
        "api_key": QWEN_API_KEY,
        "model_name": "qwen3.7-max",
        "extra_body": {},
    },
}


# ── System Prompt ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a code golf expert participating in a 30-round iterative code golf competition.

## Goal
Write the **shortest possible Python program** that defines `p(grid) -> grid` and passes ALL test cases.

## Rules
- `p` receives a nested list of ints and must return a nested list of ints (0-9 only).
- Score = UTF-8 byte count of your code (fewer = better).
- Define `p` as `def p(g):` or `p = lambda g:`.  Must be the callable name `p`.
- Standard library only.  No numpy / scipy / third-party packages.
- The judge auto-converts booleans → 0/1 and integral floats → ints (numpy.array_equal semantics).

## Strategy
1. Study the generator code — it IS the ground truth for the transformation rule.
2. **First get a correct solution** (any length), then compress aggressively.
3. In each round, try ONE optimization / new approach.  Verify by submitting.
4. If stuck, try radically different approaches: different algorithms, data structures, builtins.

## Output Format
Your reply MUST contain a single ````python` code block with your complete program.
Only the LAST python block is judged.
You may also include brief reasoning before the code block."""


# ── Prompt builders ────────────────────────────────────────────────────

def build_first_user_message(task_id: str, gen_source: str, train_display: str,
                             max_rounds: int) -> str:
    parts = [
        f"## Task: {task_id}",
        "",
        "## Generator Code (ground truth for the transformation rule)",
        "```python",
        gen_source if gen_source else "# (no generator available — infer from examples)",
        "```",
        "",
        "## Training Examples",
        train_display,
        "",
        f"## Status",
        f"Round 1 / {max_rounds}",
        "",
        "**Best so far: NONE** — you need to get ANY correct solution first.",
        "",
        "Write your code in a ```python block.  Good luck!",
    ]
    return "\n".join(parts)


def build_observation(round_no: int, max_rounds: int, status: str,
                      byte_count: int, best_bytes: "int | None",
                      error_msg: str = "", failures: list = None) -> str:
    """构造每轮的 observation（反馈给模型下一轮用）。"""
    lines = [f"## Round {round_no} / {max_rounds} — Result"]

    if status == "correct":
        is_record = best_bytes is not None and byte_count <= best_bytes
        lines.append(f"✅ **ACCEPTED** — {byte_count} bytes")
        if is_record:
            lines.append(f"🏆 **NEW BEST!** {byte_count} bytes")
        else:
            lines.append(f"(Best so far: {best_bytes} bytes)")
    elif status == "wrong":
        lines.append(f"❌ **WRONG ANSWER** — {byte_count} bytes")
        lines.append(f"Passed {len(failures) if failures else '?'} cases but failed some.")
        if best_bytes is not None:
            lines.append(f"Current best: {best_bytes} bytes")
        else:
            lines.append(f"Still no correct solution yet.")
        if failures:
            lines.append("Failures (first few):")
            for f in failures[:3]:
                lines.append(f"  - Input: {f.get('input','?')}")
                lines.append(f"    Expected: {f.get('expected','?')}")
                lines.append(f"    Got: {f.get('actual','?')}")
    elif status == "crash":
        lines.append(f"💥 **CRASH / RUNTIME ERROR** — {byte_count} bytes")
        lines.append(f"Error: {error_msg[:400]}")
        if best_bytes is not None:
            lines.append(f"Current best: {best_bytes} bytes")
        else:
            lines.append(f"Still no correct solution yet.")
    elif status == "timeout":
        lines.append(f"⏱️ **TIMEOUT** — {byte_count} bytes")
        lines.append(f"Error: {error_msg[:200]}")
        if best_bytes is not None:
            lines.append(f"Current best: {best_bytes} bytes")
        else:
            lines.append(f"Still no correct solution yet.")
    else:
        lines.append(f"⚠️ **{status.upper()}**")
        if error_msg:
            lines.append(f"Error: {error_msg[:300]}")
        if best_bytes is not None:
            lines.append(f"Current best: {best_bytes} bytes")
        else:
            lines.append(f"Still no correct solution yet.")

    lines.append("")
    lines.append("Write your next (shorter!) solution in a ```python block.")
    return "\n".join(lines)


def build_final_observation(round_no: int, max_rounds: int,
                            best_bytes: "int | None", best_code: "str | None") -> str:
    """最后一轮的 final observation（30/30 时告诉模型结束了）。"""
    if best_code is not None:
        return (
            f"## Round {round_no} / {max_rounds} — FINAL\n"
            f"🏁 **Competition over!**  Your best solution: **{best_bytes} bytes** ✅\n"
            f"```python\n{best_code}\n```"
        )
    else:
        return (
            f"## Round {round_no} / {max_rounds} — FINAL\n"
            f"🏁 **Competition over!**  Unfortunately, no correct solution was found.\n"
            f"Better luck next time!"
        )


# ── Code extraction ───────────────────────────────────────────────────

def extract_code(text: str) -> "str | None":
    """提取最后一个 ```python 代码块。"""
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    if not blocks:
        return None
    code = blocks[-1].strip()
    return code or None


# ── Train examples display ────────────────────────────────────────────

def train_to_display(train_examples, max_examples: int = 4) -> str:
    """把 train examples 格式化为展示文本。"""
    parts = []
    for i, ex in enumerate(train_examples[:max_examples], 1):
        inp = ex.input
        out = ex.output

        def grid_str(g):
            if isinstance(g, list) and g and isinstance(g[0], list):
                return "\n".join("".join(str(c) for c in row) for row in g)
            return str(g)

        parts.append(f"### Example {i}")
        parts.append(f"Input:\n{grid_str(inp)}")
        parts.append(f"Output:\n{grid_str(out)}")
    return "\n\n".join(parts)


# ── Main loop ─────────────────────────────────────────────────────────

def run(task_id: str, max_rounds: int = 30, model_key: str = "deepseek-v4-pro", seed: int = 1):
    # ── 路径 ────────────────────────────────────────────────────────
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tasks_dir = os.path.join(script_dir, "tasks")
    gen_dir = os.path.join(script_dir, "gen")

    # ── 加载任务 ─────────────────────────────────────────────────────
    from task_loader import load_task

    task_path = os.path.join(tasks_dir, f"{task_id}.json")
    if not os.path.exists(task_path):
        raise FileNotFoundError(f"Task not found: {task_path}")
    bundle = load_task(task_path, gen_dir, gen_max_chars=8000)

    # gen 目录是平铺的 taskNNN.py → 只提取 generate 函数
    gen_path = os.path.join(gen_dir, f"{task_id}.py")
    if os.path.exists(gen_path) and not bundle.has_gen:
        with open(gen_path) as f:
            gen_full = f.read()
        # 截取 generate 函数（去掉 license、import、validate）
        m = re.search(r'^def generate\(', gen_full, re.MULTILINE)
        m_end = re.search(r'^\ndef validate\(', gen_full, re.MULTILINE)
        if m and m_end:
            gen_source = gen_full[m.start():m_end.start()].strip()
        elif m:
            gen_source = gen_full[m.start():].strip()
        else:
            gen_source = gen_full
        if len(gen_source) > 8000:
            gen_source = gen_source[:8000] + "\n\n# ... (truncated)"
        bundle.gen_source = gen_source
        bundle.has_gen = True

    print(f"📦 Task: {bundle.task_id}")
    print(f"   Model: {model_key}")
    print(f"   train: {len(bundle.train)} examples")
    print(f"   hidden: {bundle.hidden_count} test cases")
    print(f"   gen.py: {'present' if bundle.has_gen else 'missing'} "
          f"({len(bundle.gen_source)} chars)")
    print()

    # ── 训练样例展示 ─────────────────────────────────────────────────
    train_display = train_to_display(bundle.train, max_examples=4)

    # ── 初始化 messages ──────────────────────────────────────────────
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_first_user_message(
            bundle.task_id, bundle.gen_source, train_display, max_rounds)},
    ]

    # ── 初始化 LLM client ────────────────────────────────────────────
    api_cfg = API_CONFIGS.get(model_key)
    if not api_cfg:
        raise ValueError(f"Unknown model: {model_key}. Options: {list(API_CONFIGS)}")

    from openai import OpenAI
    client = OpenAI(
        api_key=api_cfg["api_key"],
        base_url=api_cfg["base_url"],
    )
    model_name = api_cfg["model_name"]
    extra_body = api_cfg.get("extra_body", {})

    # ── 初始化状态 ───────────────────────────────────────────────────
    best_code = None
    best_bytes = None
    history = []
    no_improve = 0

    # ── 30 轮循环 ────────────────────────────────────────────────────
    from executor import judge

    for round_no in range(1, max_rounds + 1):
        # 提前停止：连续 no_improve_stop 轮没有改进
        if no_improve >= 5 and best_code is not None:
            print(f"\n🛑 Early stop: no improvement for {no_improve} rounds.")
            break

        print(f"🔄 Round {round_no}/{max_rounds} ...", end=" ", flush=True)
        t0 = time.time()

        # 1. 调模型
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=16384,
                extra_body=extra_body,
                timeout=180,
                seed=seed,
            )
            reply_text = response.choices[0].message.content or ""
            # DeepSeek reasoning 模式偶有空白 content
            if not reply_text:
                reasoning = getattr(response.choices[0].message, "reasoning_content", None)
                reply_text = reasoning or ""
        except Exception as e:
            print(f"❌ API error: {e}")
            history.append({"round": round_no, "status": "api_error", "error": str(e)})
            continue

        # 2. 提取代码
        code = extract_code(reply_text)
        if code is None:
            print(f"⚠️  No code block found")
            messages.append({"role": "assistant", "content": reply_text})
            obs = build_observation(round_no, max_rounds, "parse_error",
                                    0, best_bytes,
                                    error_msg="No ```python code block found in your reply.")
            messages.append({"role": "user", "content": obs})
            history.append({"round": round_no, "status": "parse_error",
                            "code": "", "bytes": 0})
            continue

        # 3. 判题
        result = judge(code, bundle)

        # 4. 更新最优
        if result.status == "correct":
            if best_bytes is None or result.byte_count < best_bytes:
                best_bytes = result.byte_count
                best_code = code
                no_improve = 0
                print(f"✅ AC {result.byte_count}B ⭐", end=" ")
            else:
                no_improve += 1
                print(f"✅ AC {result.byte_count}B", end=" ")

            # 最后一轮不追加 observation（已经结束了）
            if round_no == max_rounds:
                messages.append({"role": "assistant", "content": reply_text})
                messages.append({"role": "user", "content":
                    build_final_observation(round_no, max_rounds, best_bytes, best_code)})
        else:
            no_improve += 1
            status_map = {
                "wrong": "WA", "crash": "RE", "timeout": "TLE",
                "syntax_error": "SE", "no_p": "no_p",
            }
            short = status_map.get(result.status, result.status)
            print(f"❌ {short}", end=" ")

            if round_no == max_rounds:
                messages.append({"role": "assistant", "content": reply_text})
                messages.append({"role": "user", "content":
                    build_final_observation(round_no, max_rounds, best_bytes, best_code)})

        # 5. 追加到上下文（非最后一轮）
        if round_no < max_rounds:
            messages.append({"role": "assistant", "content": reply_text})
            obs = build_observation(
                round_no, max_rounds, result.status, result.byte_count,
                best_bytes, error_msg=result.error, failures=result.failures,
            )
            messages.append({"role": "user", "content": obs})

        # 6. 记录 history
        elapsed = time.time() - t0
        print(f"({elapsed:.1f}s)")
        history.append({
            "round": round_no,
            "code": code,
            "status": result.status,
            "bytes": result.byte_count,
            "passed": result.passed,
            "total": result.total,
            "error": result.error,
            "elapsed_s": round(elapsed, 2),
        })

    # ── 汇总 ──────────────────────────────────────────────────────────
    print()
    print("=" * 60)
    print("🏁 FINAL RESULT")
    print(f"   Task:      {task_id}")
    print(f"   Solved:    {best_code is not None}")
    print(f"   Best bytes: {best_bytes}")
    print(f"   Rounds:    {len(history)}/{max_rounds}")

    if best_code:
        print(f"   Code:")
        print(f"   {best_code}")
        print()

    return {
        "solved": best_code is not None,
        "bytes": best_bytes,
        "code": best_code,
        "history": history,
        "messages": messages,
    }


# ── CLI ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="30-round code golf agent")
    parser.add_argument("--task", default="task001", help="Task ID (default: task001)")
    parser.add_argument("--model", default="deepseek-v4-pro", choices=list(API_CONFIGS),
                        help="Model to use (default: deepseek)")
    parser.add_argument("--rounds", type=int, default=30, help="Max rounds (default: 30)")
    parser.add_argument("--seed", type=int, default=1, help="Random seed (default: 1)")
    args = parser.parse_args()

    result = run(args.task, args.rounds, args.model, args.seed)

    # 保存完整对话记录
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(os.path.dirname(__file__),
                            f"{args.model}_{args.task}_{ts}.json")
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
    print(f"📁 Trajectory saved to: {out_path}")
