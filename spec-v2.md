# Code Golf Benchmark — Agentic Loop 执行方案 v2.0

> 针对 **google-code-golf-2025**（ARC 风格 grid 变换，401 题）修订。
> 本版已消化 spec-issues.md 的全部决策点，每条决策标注 [G#] 对应 issues 文档编号。
> 语言：Python 3.11+。运行平台：macOS 开发调试，**Linux 正式跑分**（见 §2.4）。
> 默认预算：每题 30 轮 × 3 seeds。

## 决策速览（对应 issues §G 表格）

| # | 问题 | 决策 |
|---|------|------|
| 1 | I/O 模式 | **function-call `p(g)` 模式**，与官方 verify.py 一致 |
| 2 | 题目信息展示 | **注入 gen.py 全文** + 少量 train 样例（对齐人类参赛条件） |
| 3 | 判定逻辑 | **numpy.array_equal + normalize**（官方语义） |
| 4 | 三个 split | train=展示；**test + arc-gen 合并为隐藏判定集** |
| 5 | gen.py | 注入（见 #2）；common.py 默认不注入 |
| 6 | macOS | 仅开发用，沙箱走 wrapper 内 setrlimit；正式分数只认 Linux |
| 7 | 字节数 | **`os.path.getsize`**，harness 写文件前 strip 尾部空白 |
| 8 | 判定性能 | 单 subprocess 批量跑全部用例 + wrapper 内 per-case alarm |
| 9 | 错误细分 | 六级 taxonomy（§2.3） |
| 10 | early stopping | 默认无；提供 config 开关，同一榜单内必须统一 |

---

## 0. 总体架构

```
golf-bench/
├── config.yaml
├── runner.py                   # 调度 (task, model, seed) 作业矩阵
├── loop.py                     # agentic loop 核心
├── executor.py                 # 沙箱执行 + 判分
├── judge_wrapper.py            # 注入子进程的判定脚本（§2.2）
├── llm.py                      # 多模型统一客户端
├── prompts.py                  # 全部 prompt 模板
├── task_loader.py              # 读 task json + gen.py，构建 TaskBundle
├── scoring.py                  # 离线聚合
└── runs/{model}/{task_id}/seed{n}/
    ├── trajectory.jsonl
    ├── best.py
    └── meta.json
```

核心原则不变：loop 近似无状态（scratchpad + 最近历史）；一切落盘、断点续跑；判分与 loop 解耦。

## 1. 任务数据 [G1][G2][G4]

### 1.1 数据源与路径 [E1][E2]

路径全部走 config，不假设目录结构：

```yaml
tasks_dir: /path/to/google-code-golf-2025        # task001.json ... task401.json
gen_dir:   /path/to/deepseek-v4-pro-baseline     # task*/gen.py, verify.py, common.py
```

`task_loader.py` 对每题构建 `TaskBundle`：

```python
TaskBundle:
  task_id: str            # 来自文件名 "task001"
  train: list[Example]    # 展示用样例
  hidden: list[Example]   # test + arc-gen 合并，判定集
  gen_source: str         # gen.py 全文（上限 8000 字符，超出尾部截断并标注）
```

- **hidden = test + arc-gen 合并**，顺序：test 在前。判定必须全过。
- common.py **默认不注入** prompt（gen.py 中 `from common import *` 的多为数据生成随机工具，变换逻辑在 gen.py 本体）。config 留 `include_common: false` 开关；prompt 中加一句说明"gen.py 引用的 common 工具是采样辅助函数，理解变换规则不依赖它们"。
- `validate_tasks.py`：扫描 401 题，报告 train/test/arc-gen 数量分布、grid 尺寸分布、值域（确认是否全部 0-9）、gen.py 是否存在及长度、有多少 gen.py 依赖 common 中的非随机函数（抽查报告）。

### 1.2 提交接口：function-call 模式 [G1/A2]

- 模型提交一段 Python 程序，要求其中**定义可调用对象 `p`**：`p(grid) -> grid`，输入输出均为 nested list of ints。
- 判定方 import 该文件后逐用例调用 `p(ex["input"])`。
- 与官方 verify.py 及 Kaggle 人类榜完全同口径。

### 1.3 判定规则：官方语义 [G3/A3]

判定 = `numpy.array_equal(normalize(p(input)), expected)`，normalize 递归执行：

- bool → int（True→1）
- 整数值 float → int（3.0→3）；非整数值 float → 判 wrong
- tuple → list
- numpy array → list
- 其他类型（str、dict、None…）→ 判 wrong

**normalize 的实现直接从官方 verify.py 抄**，不要重新发明；如 verify.py 与上述描述有出入，以 verify.py 为准并在代码注释标注差异。

### 1.4 字节数 [G7/B3]

harness 从模型回复提取代码后：`code = code.strip()`（去首尾空白，含尾部换行），写入文件，**字节数 = `os.path.getsize(file)`**。此时等价于 `len(code.encode('utf-8'))`，且与官方 verify.py 口径一致。

附加口径：同时记录 Kaggle 官方积分 `max(1, 2500 - bytes)`，方便与人类榜直接对照。

## 2. 沙箱执行器 [G6][G8][G9]

### 2.1 批量判定架构（替代 v1 的逐用例 subprocess）[B1][F2]

一次判定 = **一个 subprocess 跑完全部用例**，流程：

1. executor 将 `{code_path, cases_path, per_case_timeout}` 传给子进程运行 `judge_wrapper.py`。
2. wrapper 内部：`importlib` 加载用户代码 → 取 `p` → 逐用例 `signal.alarm` 设 per-case 超时 → 调用、normalize、比较 → 结果流式写到 stdout（JSON lines）。
3. executor 读回结果。若子进程整体超时/崩溃，已写出的部分结果仍可用，其余用例记 `not_run`。

参数：`per_case_timeout = 2s`；子进程整体 wall-clock 上限 `min(10 + 2×n_cases, 120)s`；用户代码 import 阶段单独限 5s（import 时的顶层死循环也要能杀）。

短路策略：失败用例数达到 3 即终止（快速返回反馈）；**但当程序已正确且刷新纪录候选时不短路**（必须全过才能记纪录——实现上：默认跑全量、失败≥3 短路即可，逻辑自然满足）。

不再需要跨用例线程池（单 subprocess 内循环已经够快，n≤50、grid≤30×30 的纯计算是毫秒级）。runner 层的作业间并发不变。

### 2.2 资源限制与平台 [G6/B2]

限制在 **wrapper 子进程内自行设置**（`judge_wrapper.py` 开头调用 `resource.setrlimit`），不依赖 `preexec_fn`——这在 macOS 和 Linux 上行为一致且线程安全：

- `RLIMIT_AS = 512MB`（Linux 生效；macOS 上仅 advisory，接受）
- `RLIMIT_NPROC = 32`、`RLIMIT_FSIZE = 8MB`
- per-case 超时靠 wrapper 内 `signal.alarm`（SIGALRM 能中断纯 Python 死循环）
- 整体兜底靠 executor 侧 `subprocess timeout` + `start_new_session=True` + `os.killpg`（两平台都可靠）

平台政策：**macOS 只用于开发调试；进入 runs/ 的正式数据必须产自 Linux**（容器或服务器），meta.json 记录 `platform` 字段，scoring.py 聚合时对非 Linux 数据告警。Python 小版本固定（config `python_bin`），写进最终报告。

### 2.3 错误 taxonomy [G9/F1]

每轮判定结果为以下之一（trajectory 的 `status` 字段）：

| status | 含义 | 计入轮数 | 给模型的反馈 |
|--------|------|:-:|------|
| `parse_error` | 回复中提不出代码块 | ✓ | 提示输出格式要求 |
| `syntax_error` | 代码 compile 失败 | ✓ | SyntaxError 信息 |
| `no_p` | import 成功但无可调用 `p` | ✓ | 提示必须定义 `p` |
| `crash` | import 报错 / p() 抛异常 / 超时 / 超内存 | ✓ | traceback 尾部 500 字符 + 触发用例 |
| `wrong` | 跑通但输出不符 | ✓ | passed/ran/total + 失败样例 |
| `correct` | 全部用例通过 | ✓ | 字节数，是否刷新纪录 |
| `api_error` | API 调用失败（重试后仍失败） | ✗ | —（不进入模型视野） |

syntax check 在 executor 侧先做（`compile()`），省一次 subprocess。

## 3. Agentic Loop

### 3.1 伪代码（与 v1 一致，仅接口适配）

```
while round_no < 30 and tokens_used < budget:
    prompt = build_prompt(bundle, state)
    reply  = llm.chat(...)                 # §4
    code, notes = parse_reply(reply)
    result = judge(code, bundle.hidden)    # §2
    update best / history(最近5) / scratchpad
    append trajectory.jsonl
```

**Early stopping [G10/F3]**：默认关闭。config 提供：

```yaml
early_stop:
  no_improve_rounds: null    # 连续 N 轮 best_bytes 无下降则停（含未解出状态）
```

规则：同一榜单内所有模型该参数必须相同，meta.json 记录生效配置。建议 Phase 2 全量标定时设 15 省费用，Phase 3 主榜关闭。

### 3.2 Prompt 结构 [G2/C1]（取代 v1 §3.2）

单轮对话。**System**（全局固定，缓存前缀）+ **User** 按序拼装：

```
[A] system: golf 规则说明（function-call 接口、判定语义、字节数口径）
[B] gen.py 全文             ← 题目规则的权威定义
[C] train 样例（≤4 个）      ← 直观示例
[D] 当前状态（轮次、best_bytes、best_code）
[E] scratchpad（模型上轮笔记）
[F] 最近 3 次尝试（代码+status+反馈，按 §2.3）
[G] 输出格式要求
```

**Grid 展示格式**：值域确认为 0-9 时，每行 digits 直接连写、行间换行、样例间空行标注 `Input:`/`Output:`（token 最省且无歧义）；若 validate 发现超出 0-9 的题，该题降级为 JSON 展示。

**Train 样例选取**：按 grid 面积（rows×cols）排序取最小、中位、最大共 3 个；单样例文本超 1500 字符则跳过顺延；prompt 总预算内放不下就减到 2 个、1 个。有 gen.py 在场，样例只是辅助，不必求全。

**Caching [C3]**：稳定前缀 = system + [B] + [C]（同一作业 30 轮内不变，Anthropic 打 `cache_control`，OpenAI 类自动命中）。跨 task 不共享是预期行为，30 轮内命中已覆盖大头。

### 3.3 输出格式 [C2]

```
<notes>
（≤500 token：规则理解、已试思路、失败原因、下一步计划）
</notes>

```python
p=lambda g: ...   # 或 def p(g): ...
```
```

解析：取最后一个 ```python 块；notes 缺失沿用旧值；均缺 → parse_error。

## 4. LLM 客户端 [G-D1][G-D2]

### 4.1 config 完整示例

```yaml
models:
  deepseek-v4-pro:
    provider: openai_compatible
    base_url: https://api.deepseek.com/v1
    model_name: deepseek-reasoner
    api_key_env: DEEPSEEK_API_KEY
    max_concurrency: 8
    max_output_tokens: 16384
    extra_body: {thinking: {type: enabled}}     # 原样透传
    price_per_mtok: {input: 0.27, output: 1.10, cached_input: 0.027}
  claude-sonnet:
    provider: anthropic
    model_name: claude-sonnet-4-5
    api_key_env: ANTHROPIC_API_KEY
    max_concurrency: 4
    max_output_tokens: 16384
    cache_system_prefix: true                    # 对稳定前缀打 cache_control
    price_per_mtok: {input: 3.0, output: 15.0, cached_input: 0.3}
```

### 4.2 重试与错误分类

- **可重试**（指数退避 1/2/4/8/16s，5 次）：408、429、5xx、连接错误、读超时。
- **不可重试**（立即中止整个作业并标记 `config_error`）：400、401、403、404、422——这些是配置问题，重试无意义，且要快速暴露。
- **空 content**（DeepSeek reasoning 模式偶发只有 reasoning_content 无 content）：视为可重试，最多 2 次；仍空则记 `parse_error` 计入轮数。若 `reasoning_content` 非空，先尝试从中提取代码块，提取成功按正常轮处理。
- 连续 10 次 api_error → 作业 failed，runner 继续其他作业。

## 5. 产物格式

trajectory.jsonl 每行新增/调整字段：`status`（§2.3 七值）、`kaggle_score`。
meta.json 新增：`platform`（uname）、`python_version`、`early_stop_config`、`kaggle_score_best`。其余同 v1。

## 6. 离线聚合（scoring.py）

- 单题分 `score = record_bytes / best_bytes`（未解出=0），record 为池记录，可选并入 Kaggle 人类纪录做锚点（config 开关，两种口径都输出）。
- 汇总指标：solve_rate、golf_score、kaggle_total（官方积分制总分，直接可比人类榜）、mean_first_correct_round、bytes 曲线 AUC。
- best-of-3 与 median-of-3 两口径。输出 leaderboard.csv + per_task.csv。

## 7. 验收测试（更新）

1. `validate_tasks.py` 通过：401 题 schema 一致、值域报告、gen.py 覆盖率。
2. executor：死循环 p（import 时 / 调用时两种）被 alarm 杀掉且不拖垮整批；内存炸弹（Linux 上）触发限制；返回部分结果的崩溃场景可解析。
3. normalize 与官方 verify.py 对拍：随机抽 20 题，用官方 verify.py 和我们的 judge 分别判同一批提交（含构造的 bool/float/tuple 输出），结果必须完全一致。**这是最重要的一条验收。**
4. loop 端到端 mock 测试 + 断点续跑（同 v1）。
5. 七种 status 各构造一个用例验证 trajectory 记录与反馈文本。

## 8. 分阶段计划（不变）

Phase 0 实现+验收 → Phase 1 pilot（1 模型 × 10 题 × 1 seed，人工审 trajectory）→ Phase 2 便宜模型全量标定 + 筛 Core 集 → Phase 3 主榜（含 GPT/Claude，Linux + batch + caching）。

---

## 附：v1 → v2 变更摘要

- I/O 从 stdin/stdout 改为 `p(grid)` function-call（对齐官方）
- 判定从文本匹配改为 numpy.array_equal + normalize（实现从 verify.py 抄，并加对拍验收）
- prompt 题面从 description 改为 gen.py 全文 + 少量 train 样例（对齐人类参赛信息条件）
- 判定从逐用例 subprocess 改为单进程批量 + wrapper 内 alarm（性能）
- 资源限制从 preexec_fn 移入 wrapper 自身（macOS 兼容）；正式数据仅认 Linux
- 字节数统一为文件 getsize（写前 strip）；新增 Kaggle 积分口径
- 错误细分七级 taxonomy；API 错误区分可重试/不可重试；处理 DeepSeek 空 content
- 路径全部 config 化；early stopping 作为 config 开关默认关闭