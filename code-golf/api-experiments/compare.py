#!/usr/bin/env python3
"""Multi-model comparison: N trials per model per task.

Usage: python3 compare.py [tasks] [trials] [prompt-file]
       python3 compare.py 1-10 5 prompt-no.md
"""
import json, os, re, statistics, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from openai import OpenAI

DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(DIR)
TASKS_DIR = f"{ROOT}/google-code-golf-2025"

# model -> (base_url, extra request kwargs)
MODELS = {
    "deepseek-v4-pro": ("https://api.deepseek.com",
                        dict(reasoning_effort="high",
                             extra_body={"thinking": {"type": "enabled"}})),
}

# api.md name -> model id used on the endpoint
KEY_ALIAS = {"qwen3.7-max": "qwen-3.7-max"}


def load_keys():
    keys = {}
    for line in open(f"{DIR}/env/api.md"):
        if ":" in line:
            name, key = line.split(":", 1)
            keys[name.strip()] = key.strip()
    return keys


def grid(g):
    return "\n".join(" ".join(map(str, r)) for r in g)


def build_prompt(task, tpl_file):
    tpl = open(f"{DIR}/{tpl_file}").read()
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


def trial(client, model, extra, task, k, run_dir, prompt):
    d = f"{run_dir}/{task}/{model}/trial_{k}"
    os.makedirs(d, exist_ok=True)
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful assistant"},
                      {"role": "user", "content": prompt}],
            stream=False, **extra)
        out = resp.choices[0].message.content or ""
        open(f"{d}/output.md", "w").write(out)
        code = parse_code(out)
        open(f"{d}/solution.py", "w").write(code)
        v = verify(f"{d}/solution.py", task)
        rec = {"task": task, "model": model, "trial": k, "correct": v["correct"],
               "passed": f"{v['passed']}/{v['total']}",
               "bytes": len(code.encode()), "seconds": round(time.time() - t0, 1)}
    except Exception as e:
        rec = {"task": task, "model": model, "trial": k, "correct": False,
               "error": str(e)[:200], "seconds": round(time.time() - t0, 1)}
    print(rec, flush=True)
    return rec


def main():
    spec = sys.argv[1] if len(sys.argv) > 1 else "1"
    trials = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    tpl_file = sys.argv[3] if len(sys.argv) > 3 else "prompt.md"

    tasks = []
    for p in spec.split(","):
        a, _, b = p.partition("-")
        tasks += [f"task{int(i):03d}" for i in range(int(a), int(b or a) + 1)]

    keys = load_keys()
    clients = {m: OpenAI(api_key=keys[KEY_ALIAS.get(m, m)], base_url=url,
                         timeout=900, max_retries=2)
               for m, (url, _) in MODELS.items()}

    run_dir = f"{DIR}/runs/compare-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    prompts = {}
    for t in tasks:
        prompts[t] = build_prompt(t, tpl_file)
        os.makedirs(f"{run_dir}/{t}", exist_ok=True)
        open(f"{run_dir}/{t}/prompt.md", "w").write(prompts[t])
    json.dump({"tasks": tasks, "trials": trials, "prompt": tpl_file},
              open(f"{run_dir}/meta.json", "w"))

    # models innermost so parallel slots spread across providers
    jobs = [(t, m, k) for k in range(1, trials + 1) for t in tasks for m in MODELS]
    with ThreadPoolExecutor(12) as pool:
        results = list(pool.map(
            lambda j: trial(clients[j[1]], j[1], MODELS[j[1]][1], j[0], j[2],
                            run_dir, prompts[j[0]]),
            jobs))

    json.dump(results, open(f"{run_dir}/results.json", "w"), indent=2)

    print(f"\n── {len(tasks)} task(s) × {trials} trials/model, prompt={tpl_file} ──")
    print(f"{'Task':<10}" + "".join(f"{m:<26}" for m in MODELS))
    for t in tasks:
        row = f"{t:<10}"
        for m in MODELS:
            ok = [r["bytes"] for r in results
                  if r["task"] == t and r["model"] == m and r.get("correct")]
            n = sum(1 for r in results if r["task"] == t and r["model"] == m)
            cell = f"{len(ok)}/{n}"
            if ok:
                cell += f" min{min(ok)} avg{statistics.mean(ok):.0f}"
            row += f"{cell:<26}"
        print(row)
    for m in MODELS:
        ok = sum(1 for r in results if r["model"] == m and r.get("correct"))
        n = sum(1 for r in results if r["model"] == m)
        print(f"{m}: {ok}/{n} correct ({ok/n:.0%})")
    print(f"\nResults: {run_dir}/results.json")


if __name__ == "__main__":
    main()
