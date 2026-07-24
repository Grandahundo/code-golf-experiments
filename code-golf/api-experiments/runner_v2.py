#!/usr/bin/env python3
"""Simple runner: prompt -> API -> save raw output -> parse code -> verify.

Usage: python3 runner_v2.py [tasks] [trials]     # default: 1-10 5
"""
import json, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from openai import OpenAI

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)
TASKS_DIR = f"{ROOT}/google-code-golf-2025"
MODEL = "deepseek-v4-pro"

client = OpenAI(api_key=open(f"{ROOT}/env/deepseek-api.md").read().strip(),
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


def parse_code(text):
    m = re.findall(r"```(?:python)?\n(.*?)```", text, re.S)
    return (m[-1] if m else text).strip() + "\n"


def verify(code_file, task):
    r = subprocess.run(
        [sys.executable, f"{DIR}/harness.py", code_file, f"{TASKS_DIR}/{task}.json"],
        capture_output=True, text=True, timeout=30)
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"correct": False, "passed": 0, "total": 0}


def trial(run_dir, task, k, prompt):
    d = f"{run_dir}/{task}/trial_{k}"
    os.makedirs(d, exist_ok=True)
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": "You are a helpful assistant"},
                      {"role": "user", "content": prompt}],
            stream=False,
            reasoning_effort="high",
            extra_body={"thinking": {"type": "enabled"}})
        out = resp.choices[0].message.content or ""
        open(f"{d}/output.md", "w").write(out)      # 模型直接输出的结果
        code = parse_code(out)
        open(f"{d}/solution.py", "w").write(code)
        v = verify(f"{d}/solution.py", task)
        rec = {"task": task, "trial": k, "correct": v["correct"],
               "passed": f"{v['passed']}/{v['total']}",
               "bytes": len(code.encode()), "seconds": round(time.time() - t0, 1)}
    except Exception as e:
        rec = {"task": task, "trial": k, "correct": False, "error": str(e),
               "seconds": round(time.time() - t0, 1)}
    print(rec, flush=True)
    return rec


def main():
    spec = sys.argv[1] if len(sys.argv) > 1 else "1-10"
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    tasks = []
    for p in spec.split(","):
        a, _, b = p.partition("-")
        tasks += [f"task{int(i):03d}" for i in range(int(a), int(b or a) + 1)]

    run_dir = f"{DIR}/runs/" + datetime.now().strftime("%Y%m%d-%H%M%S")
    prompts = {}
    for t in tasks:
        os.makedirs(f"{run_dir}/{t}", exist_ok=True)
        prompts[t] = build_prompt(t)
        open(f"{run_dir}/{t}/prompt.md", "w").write(prompts[t])

    jobs = [(t, k) for t in tasks for k in range(1, trials + 1)]
    with ThreadPoolExecutor(5) as pool:
        results = list(pool.map(lambda j: trial(run_dir, j[0], j[1], prompts[j[0]]), jobs))

    json.dump(results, open(f"{run_dir}/results.json", "w"), indent=2)
    print()
    for t in tasks:
        rs = [r for r in results if r["task"] == t]
        ok = [r for r in rs if r.get("correct")]
        best = min((r["bytes"] for r in ok), default="-")
        print(f"{t}: {len(ok)}/{len(rs)} correct, best {best}B")
    print(f"\nResults: {run_dir}/results.json")


if __name__ == "__main__":
    main()
