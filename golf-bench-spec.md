# Code Golf Benchmark — Agentic Loop 执行方案 v1.0

> 本文档是完整实现规格，可直接交给编码模型实现。语言：Python 3.11+。
> 被测程序语言：Python。执行隔离：subprocess + 资源限制。
> 默认预算：每题 30 轮 × 3 seeds。

---

## 0. 总体架构

```
golf-bench/
├── tasks/                      # 题目数据（已有）
│   ├── task001.json
│   ├── task002.json
│   └── ...
├── config.yaml                 # 全局配置
├── runner.py                   # 入口：调度所有 (task, model, seed) 作业
├── loop.py                     # 单个作业的 agentic loop 核心
├── executor.py                 # 沙箱执行 + 判分
├── llm.py                      # 统一的多模型 API 客户端
├── prompts.py                  # 所有 prompt 模板（集中管理，勿散落各处）
├── scoring.py                  # 离线聚合：从 runs/ 计算榜单
└── runs/                       # 输出（按作业隔离，见 §7）
    └── {model}/{task_id}/seed{n}/
        ├── trajectory.jsonl    # 每轮记录
        ├── best.py             # 当前最优程序
        └── meta.json           # 作业级摘要
```

核心原则：

1. **Loop 近似无状态**：每轮 context 重新构建，只包含题面、当前最优解、最近 K 次尝试、模型自维护的 scratchpad。单轮 context 恒定在 ~10k token，总消耗随轮数线性增长，永不爆 context。
2. **一切落盘、可断点续跑**：任何作业中断后，重跑 runner 时从 trajectory.jsonl 恢复，不重复消耗 API 费用。
3. **判分逻辑与 loop 解耦**：executor 是纯函数（程序 + 测试集 → 判定结果），可单独测试。

---

## 1. 任务数据格式

### 1.1 输入：task{k}.json（已有）

假定结构（实现时以实际文件为准，写一个 `validate_tasks.py` 先扫一遍全部 400 个文件确认字段一致性）：

```json
{
  "task_id": "task001",
  "description": "题目描述文本",
  "test_cases": [
    {"input": "...", "output": "..."},
    ...   // 可能有几十到上千个，文件很大
  ]
}
```

### 1.2 测试集切分（关键设计）

每题的 test_cases 切成两部分，**切分在首次加载时确定并缓存到 `tasks_split/{task_id}.json`，此后永不变动**（保证所有模型、所有 seed 面对完全相同的切分）：

- **公开示例集 `examples`**：取 3 个用例展示给模型。选取规则：按 `len(input)` 排序后取最短的 1 个、中位的 1 个、最长的 1 个（覆盖规模范围；若不足 3 个则全取）。单个用例的 input/output 若超过 800 字符，该用例跳过、顺延选下一个；若全部超长，则截断展示并标注 `...(truncated, full length: N chars)`。
- **完整判定集 `full`**：全部 test_cases（包含示例）。判分永远用完整集，示例只用于展示。

切分用固定 seed 的确定性算法，不用随机。

### 1.3 判定规则（写死，全局统一）

- 逐用例比较：`actual.rstrip('\n') == expected.rstrip('\n')`，即仅忽略**末尾换行差异**，其余（含行内尾随空格）严格匹配。
- 程序通过 stdin 读输入，stdout 写输出。stderr 忽略（不参与判定，但记录）。
- 全部用例通过才算 correct。

---

## 2. 沙箱执行器（executor.py）

### 2.1 单次运行

```python
def run_program(code: str, stdin_data: str, timeout_s: float = 5.0,
                memory_mb: int = 256) -> RunResult
```

实现要点：

- `subprocess.run([PYTHON_BIN, script_path], input=..., capture_output=True, timeout=...)`，其中 `PYTHON_BIN` 来自 config（指定一个固定小版本，如 python3.11，写进最终报告）。
- 代码写入临时文件执行（不用 `-c`，避免超长命令行和引号问题）。**字节数以 UTF-8 编码的文件字节数计**（`len(code.encode('utf-8'))`），末尾恰好一个换行符不计入（golf 惯例）。
- 子进程内用 `preexec_fn` 设置 `resource.setrlimit`：`RLIMIT_AS = memory_mb` 上限、`RLIMIT_CPU = timeout_s + 1`、`RLIMIT_NPROC = 16`（防 fork 炸弹）、`RLIMIT_FSIZE = 8MB`（防写盘）。
- 环境变量清空为最小集（`PATH` 等必需项），工作目录为空临时目录。
- 超时 kill 整个进程组（`start_new_session=True` + `os.killpg`）。
- 返回：`{status: ok|timeout|runtime_error|memory_error, stdout, stderr, elapsed}`。stdout 捕获上限 2MB，超出即判 wrong（防输出轰炸）。

### 2.2 整题判定

```python
def judge(code: str, task_split: TaskSplit) -> JudgeResult
```

- 逐用例运行。**短路策略**：先跑 3 个示例用例，全过再跑完整集；完整集中失败数达到 3 个即停止（省时间）。
- 完整集很大时，同一程序的多个用例可用线程池并发跑（subprocess 释放 GIL，并发 8 路）。
- 返回结构：

```json
{
  "correct": false,
  "passed": 41, "total": 200, "ran": 44,
  "byte_count": 87,
  "failures": [
    {"input": "...", "expected": "...", "actual": "...", "status": "wrong_output"},
    ...   // 最多保留 3 个，每个字段截断到 500 字符
  ]
}
```

- `failures` 中优先放**输入最短**的失败用例（短反例对模型 debug 价值最高）。

---

## 3. Agentic Loop（loop.py）

### 3.1 单作业伪代码

```
def run_job(task, model, seed, max_rounds=30, token_budget=1_500_000):
    state = restore_from_disk() or init_state()
    # state: round_no, best_code, best_bytes, history(最近5轮), scratchpad, tokens_used

    while state.round_no < max_rounds and state.tokens_used < token_budget:
        prompt = build_prompt(task, state)          # §3.2
        reply  = llm.chat(model, prompt, temperature=0.7, seed=seed)
        code, scratchpad = parse_reply(reply)        # §3.3
        if code is None:
            record_round(status="parse_error"); continue   # 计入轮数
        result = judge(code, task.split)
        if result.correct and result.byte_count < state.best_bytes:
            state.best_code, state.best_bytes = code, result.byte_count
        state.scratchpad = scratchpad
        state.history.append((code, result))         # 只保留最近 5 条
        record_round(...)                            # 追加写 trajectory.jsonl
    write_meta()
```

细节规定：

- **温度 0.7**，所有模型一致。API 支持 seed 参数的就传 seed（不支持的忽略，seed 仍用于目录命名区分重复实验）。
- **token_budget** 为兜底防失控，默认 1.5M（约为 30 轮正常消耗的 3 倍），从 API 返回的 usage 累加。
- API 调用失败：指数退避重试 5 次（1/2/4/8/16s）；仍失败则该轮记 `api_error`，**不计入轮数**，连续 10 次 api_error 则作业标记 failed 退出。
- parse_error（回复中提不出代码）**计入轮数**——这是模型自己的问题，属于能力的一部分。

### 3.2 每轮 Prompt 构建（build_prompt）

每轮都是**全新的单轮对话**（system + 一条 user message），不携带 API 层面的多轮历史。user message 按以下顺序拼装：

```
[A] 任务说明与规则（固定文本，见 §6 模板）
[B] 题目描述（task.description 原文）
[C] 3 个公开示例用例（input/output 原样展示，代码块包裹）
[D] 当前状态：
    - 第 {round_no+1}/{max_rounds} 轮
    - 当前最优：{best_bytes} 字节（附 best_code 原文）；若尚无正确解则明确说明
[E] 你的笔记（scratchpad，上一轮模型自己写的，原样注入；首轮为空）
[F] 最近尝试历史（最多 3 条，每条含：代码、字节数、判定摘要、失败样例）
[G] 输出格式要求（固定文本，见 §6 模板）
```

历史条目中的代码若超过 2000 字符则截断中间部分。整个 prompt 若估算超过 20k token（字符数/3 粗估），从最旧的历史条目开始丢弃。

**Prompt caching**：[A] 放在 system message 里且完全固定，[B][C] 在同一作业内不变——把 `system + [B][C]` 作为稳定前缀，对支持 prompt caching 的 API（Anthropic 显式 cache_control、OpenAI 自动）能命中缓存。可变部分 [D]-[G] 放在后面。

### 3.3 回复解析（parse_reply）

要求模型按固定格式输出（在 [G] 中规定）：

````
<notes>
（更新后的笔记，≤500 token：已试思路、失败原因、下一步计划）
</notes>

```python
（完整程序）
```
````

解析规则：取回复中**最后一个** ```python 代码块作为提交程序（模型常在正文里写草稿代码，最后一个才是答案）；`<notes>...</notes>` 作为新 scratchpad，缺失则沿用旧的。两者都提不出 → parse_error。scratchpad 超 3000 字符则尾部截断。

### 3.4 反馈内容（注入下一轮 [F] 的判定摘要）

- 正确：`✓ 正确，{bytes} 字节`（若刷新纪录则注明）。
- 错误：`✗ 通过 {passed}/{ran}（共 {total} 个用例）` + 最多 3 个失败样例（input / expected / actual，各截断 500 字符）。
- 超时/运行时错误：状态 + stderr 尾部 500 字符。

---

## 4. 调度器（runner.py）

- 作业矩阵 = tasks × models × seeds，全部作业写入一个清单，逐个检查 `meta.json` 是否已完成，未完成的入队。
- 并发：`asyncio` + 每模型独立的信号量（`config: model.max_concurrency`，默认 8），避免单一 provider 限流拖垮全局。判分部分放线程池。
- 命令行接口：

```
python runner.py --config config.yaml \
    --models deepseek-v4,glm-5 \
    --tasks tasks/core100.txt \      # 题目 id 列表文件，缺省=全部
    --seeds 3 \
    --dry-run                        # 只打印作业清单和预估费用
```

- 优雅中断：Ctrl-C 后等待当前轮写盘完成再退出。
- 全局进度：每 60s 打印一行汇总（完成作业数 / 总数、累计 token、累计费用估算）。

## 5. 配置（config.yaml）

```yaml
python_bin: python3.11
max_rounds: 30
history_window: 3        # 注入 prompt 的最近尝试数
temperature: 0.7
timeout_s: 5.0
memory_mb: 256
token_budget_per_job: 1500000

models:
  deepseek-v4:
    provider: openai_compatible
    base_url: https://api.deepseek.com/v1
    model_name: deepseek-chat
    api_key_env: DEEPSEEK_API_KEY
    max_concurrency: 8
    price_per_mtok: {input: 0.27, output: 1.10, cached_input: 0.027}
  claude-sonnet:
    provider: anthropic
    ...
```

llm.py 对上层暴露统一接口 `chat(model_cfg, system, user, temperature, seed) -> (text, usage)`，内部按 provider 分发（openai_compatible / anthropic 两种即可覆盖绝大多数模型）。

---

## 6. Prompt 模板（prompts.py）

> ⚠️ 此处为占位初稿。正式版模板由我方提供（现有 prompt 优化后替换），实现时只需保证模板变量齐全：
> `{round_no} {max_rounds} {description} {examples} {best_bytes} {best_code} {scratchpad} {history}`

**System（固定，作为缓存前缀）：**

```
你是一位 code golf 专家。你的任务是编写一个尽可能短的 Python 程序解决给定问题。

规则：
- 程序从标准输入读取数据，向标准输出写结果
- 判定标准：所有隐藏测试用例的输出与标准答案完全一致（仅忽略末尾换行）
- 分数 = 程序的 UTF-8 字节数，越短越好；但错误的程序得 0 分
- 首要目标是先得到正确解，然后逐轮压缩
- 每轮你会看到上一轮的判定结果和失败样例
```

**User（每轮重建）：** 按 §3.2 的 [B]-[G] 拼装，[G] 固定为：

```
请先在 <notes>...</notes> 中更新你的笔记（500 token 以内：记录已试思路、
失败原因、下一步计划——下一轮你只能看到这份笔记和最近 3 次尝试），
然后给出完整程序，放在回复最后的 ```python 代码块中。
```

---

## 7. 日志与产物格式

**trajectory.jsonl**（每轮一行，追加写）：

```json
{"round": 5, "ts": "2026-07-17T10:23:01Z", "code": "...", "byte_count": 87,
 "correct": false, "passed": 41, "ran": 44, "total": 200,
 "failures_shown": [...], "scratchpad": "...",
 "usage": {"input": 8123, "output": 1450, "cached": 6200},
 "status": "judged"}    // judged | parse_error | api_error
```

**meta.json**（作业结束时写）：

```json
{"task_id": "task001", "model": "deepseek-v4", "seed": 1,
 "finished": true, "rounds_used": 30,
 "first_correct_round": 4, "best_bytes": 62, "best_code": "...",
 "bytes_curve": [null, null, null, 131, 131, 98, ...],   // 每轮结束时的 best_bytes
 "total_usage": {...}, "wall_time_s": 1834}
```

## 8. 离线聚合（scoring.py）

从 runs/ 目录读取全部 meta.json，输出：

- **单题单模型分**：`score = record_bytes / best_bytes`（未解出 = 0）。`record_bytes` = 该题全体模型全体 seeds 的历史最短（池记录），存于 `records.json` 并随每次聚合滚动更新。
- 每模型报告（best-of-3-seeds 与 median-of-3 两个口径）：`solve_rate`（≥1 个正确解的题目占比）、`golf_score`（全题平均 score）、`mean_first_correct_round`、AUC（bytes_curve 归一化后的曲线下面积）。
- 输出 `leaderboard.csv` + 每题明细 `per_task.csv`。

## 9. 验收测试（实现方必须提供）

1. `validate_tasks.py` 扫描全部 task json，报告字段缺失/格式异常。
2. executor 单测：死循环程序 5s 内被杀；`while 1: a=[0]*10**6` 触发内存限制；fork 炸弹被拦；`print` 大量输出被截断判 wrong。
3. loop 端到端测试：用一个 mock LLM（固定返回预设回复序列）跑通 5 轮，验证 trajectory/meta 格式、断点续跑（中途 kill 后重跑不重复调用）。
4. 判分正确性：手工构造 3 组（正确解 / 差一个换行的解 / 部分错误解）验证 judge 输出。

## 10. 分阶段执行计划

1. **Phase 0（实现 + 验收）**：完成上述全部模块，通过 §9 验收。
2. **Phase 1（pilot）**：1 个便宜模型 × 10 题 × 1 seed，人工检查 trajectory：反馈是否有效、模型是否在正常压缩、30 轮是否够用、费用与预估是否吻合。据此调参。
3. **Phase 2（全量标定）**：2-3 个便宜模型 × 400 题 × 3 seeds → 难度标定 + 筛选 Core-100。
4. **Phase 3（主榜）**：全部模型（含 GPT/Claude，用 batch + caching）× Core-100 × 3 seeds。
