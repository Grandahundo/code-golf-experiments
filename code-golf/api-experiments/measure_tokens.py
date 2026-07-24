#!/usr/bin/env python3
"""Quick token measurement: 3 tasks x 2 trials, capture full usage info."""
import json, os, re, sys, time
from openai import OpenAI

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)
TASKS_DIR = f"{ROOT}/google-code-golf-2025"

client = OpenAI(
    api_key=open(f"{ROOT}/env/deepseek-api.md").read().strip(),
    base_url="https://api.deepseek.com")

def grid(g):
    return "\n".join(" ".join(map(str, r)) for r in g)

def build_prompt(task):
    tpl = open(f"{DIR}/prompt.md").read()
    head = tpl[:tpl.find("## Example")].replace("task001", task)
    data = json.load(open(f"{TASKS_DIR}/{task}.json"))
    return head + "\n\n".join(
        f"## Example {i}  (input {len(e['input'])}x{len(e['input'][0])} -> "
        f"output {len(e['output'])}x{len(e['output'][0])})\n"
        f"Input:\n{grid(e['input'])}\nOutput:\n{grid(e['output'])}"
        for i, e in enumerate(data["train"], 1))

TASKS = ["task001", "task005", "task007"]  # easy, hard, medium
TRIALS = 2

print("=" * 80)
print("  DeepSeek v4 Pro — Token Measurement (3 tasks × 2 trials)")
print("=" * 80)
print()

total_prompt_tok = 0
total_completion_tok = 0
total_reasoning_tok = 0
total_tok = 0

for task in TASKS:
    prompt = build_prompt(task)
    prompt_chars = len(prompt)

    for k in range(1, TRIALS + 1):
        t0 = time.time()
        resp = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "system", "content": "You are a helpful assistant"},
                      {"role": "user", "content": prompt}],
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}})
        elapsed = time.time() - t0

        usage = resp.usage
        out_text = resp.choices[0].message.content or ""
        code_match = re.findall(r"```(?:python)?\n(.*?)```", out_text, re.S)
        code = (code_match[-1] if code_match else out_text).strip()
        code_bytes = len(code.encode())

        # Get reasoning tokens
        reasoning_tok = getattr(usage, 'completion_tokens_details', None)
        if reasoning_tok and hasattr(reasoning_tok, 'reasoning_tokens'):
            reasoning_tok = reasoning_tok.reasoning_tokens
        else:
            reasoning_tok = 0

        completion_tok = usage.completion_tokens
        prompt_tok = usage.prompt_tokens
        total_call = usage.total_tokens

        total_prompt_tok += prompt_tok
        total_completion_tok += completion_tok
        total_reasoning_tok += reasoning_tok
        total_tok += total_call

        print(f"  {task} trial {k}:")
        print(f"    prompt tokens:      {prompt_tok:>8,}")
        print(f"    completion tokens:  {completion_tok:>8,}")
        print(f"      of which reasoning: {reasoning_tok:>8,} (free)")
        print(f"    total tokens:       {total_call:>8,}")
        print(f"    code: {code_bytes}B  |  time: {elapsed:.0f}s")
        print(f"    output chars: {len(out_text):,} (prompt chars: {prompt_chars:,})")
        print()

print("=" * 80)
print(f"  SUMMARY (6 calls total)")
print(f"    total prompt tokens:       {total_prompt_tok:>10,}")
print(f"    total completion tokens:   {total_completion_tok:>10,}")
print(f"      of which reasoning:      {total_reasoning_tok:>10,} (free)")
print(f"    billed completion tokens:  {total_completion_tok - total_reasoning_tok:>10,}")
print(f"    TOTAL tokens:              {total_tok:>10,}")
print()
print(f"  Extrapolated to 50 calls (×8.33):")
print(f"    prompt:     ~{total_prompt_tok * 50 / 6:,.0f}")
print(f"    completion: ~{total_completion_tok * 50 / 6:,.0f}")
print(f"    reasoning:  ~{total_reasoning_tok * 50 / 6:,.0f}")
print(f"    total:      ~{total_tok * 50 / 6:,.0f}")
