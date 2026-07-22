# Spec vs Reality — Issues & Decision Points

> 本文档列出 golf-bench-spec.md 与实际任务数据之间的所有差异、以及 spec 内部未明确的决策点。供修改 spec 时逐条核对。

---

## A. 任务数据格式（§1 — 根本性差异）

### A1. 顶层结构完全不同

**Spec 假设:**
```json
{
  "task_id": "task001",
  "description": "题目描述文本",
  "test_cases": [
    {"input": "...", "output": "..."}
  ]
}
```

**实际（google-code-golf-2025 的 401 个文件）:**
```json
{
  "train": [
    {"input": [[0,0,5],[0,5,0],[5,0,0]], "output": [[3,3,3],[4,4,4],[2,2,2]]}
  ],
  "test": [
    {"input": [[0,0,5],[5,0,0],[0,5,0]], "output": [[3,3,3],[2,2,2],[4,4,4]]}
  ],
  "arc-gen": [
    {"input": [...], "output": [...]}
  ]
}
```

**差异:**
- 没有 `task_id` 顶层字段（id 来自文件名 `task001.json`）
- 没有 `description` 字段（题目意图需从 train 样例推断）
- `test_cases` 不存在，取而代之的是 `train` / `test` / `arc-gen` 三个 split
- I/O 不是字符串，是 nested list of ints（grid）

**建议 spec 修改方向:**
- 承认两种任务格式并存，或明确只支持 grid 格式
- 重新定义字段名和 schema

---

### A2. I/O 接口模型：函数调用 vs stdin/stdout

**Spec 说:** 程序从 stdin 读输入，向 stdout 写输出

**实际:** 程序定义一个 `p(input)` 可调用对象（函数/lambda），接收 nested list，返回 nested list。验证方 `import` 用户代码后调用 `p(ex["input"])`，用 `numpy.array_equal` 比较。

**影响范围:**
- executor.py 的 `run_program()` 签名和实现完全不同
- prompt 中的规则说明需要改（告诉模型定义 `p` 而不是读 stdin）
- 判分脚本需要 import 用户代码而非 subprocess pipe

**建议 spec 修改方向:**
- 明确采用 function-call 模式
- 或者增加适配层，但会增加复杂度

---

### A3. 判定逻辑：结构化比对 vs 文本比对

**Spec 说:** `actual.rstrip('\n') == expected.rstrip('\n')`，严格匹配（仅忽略末尾换行）

**实际:** `numpy.array_equal(normalize(actual), expected)`，其中 normalize 会：
- 把 bool → int（True→1, False→0）
- 把 float → int（3.0→3）
- 把 tuple → list
- 递归处理 nested structure

这是一个**容忍型匹配**，不是严格文本比对。

**建议 spec 修改方向:**
- 明确判定规则为 numpy.array_equal 语义
- 说明 normalize 的具体转换规则

---

### A4. 测试集切分（§1.2）

**Spec 说:** test_cases 按 len(input) 排序取 3 个做示例

**实际:** 数据已经天然分成了 `train`（2-12 个样例）和 `test`（1-~50 个隐藏用例）+ `arc-gen`（生成器生成的额外用例）。

**差异:**
- 不需要"切分"，train 就是示例来源，test 就是判定集
- 示例数量远超 3 个，且全部展示可能太长
- 需要新的示例选择策略（按 grid 大小截断？逐个展示直到 token 预算？）

**建议 spec 修改方向:**
- 重新定义示例选取规则
- 明确 train/test/arc-gen 三个 split 各自用途

---

## B. 执行器（§2 — 实现细节差异）

### B1. 执行方式

**Spec 说:** 写临时 .py 文件 → `subprocess.run` 传 stdin → 读 stdout

**实际需要:** 写临时 .py 文件 → 子进程中 import → 逐用例调用 `p(input)` → 收集结果

两种方案:
- **方案 A**: 子进程 import 方案（匹配现有 harness.py）。优点：和 verify.py 一致。缺点：import 有开销，错误处理更复杂
- **方案 B**: stdin/stdout 适配层。包装成 `print(p(json.loads(sys.stdin.read())))`。优点：保持 spec 架构。缺点：序列化/反序列化开销，大 grid 的 JSON 解析可能慢

**建议 spec 修改方向:** 明确选一种

---

### B2. 资源限制细节

**Spec 说:** `RLIMIT_AS`、`RLIMIT_CPU`、`RLIMIT_NPROC=16`、`RLIMIT_FSIZE=8MB`

这些在 macOS 上的行为:
- `RLIMIT_AS` 在 macOS 上**不完全生效**（macOS 用 `RLIMIT_RSS` 但也是 advisory）
- `RLIMIT_CPU` 对纯 Python 死循环有效，但对 C 扩展不一定
- `preexec_fn` 在多线程 + macOS 上不可靠（macOS 不支持 `preexec_fn`，只支持 `start_new_session`）

**建议:** spec 需要注明平台差异，或者提供 macOS fallback（如 `resource.setrlimit` 在主进程设置后 fork）

---

### B3. 字节数计算

**Spec 说:** `len(code.encode('utf-8'))`，末尾恰好一个换行不计入

**实际（verify.py）:** 直接读文件字节数（`os.path.getsize`），不做换行处理

**差异:** 如果模型输出末尾无换行，两种算法等价。如果有多个换行，结果不同。

**建议:** 统一为 `os.path.getsize`（文件字节数），和现有 verify.py 一致

---

## C. Prompt & Loop（§3、§6 — 结构差异）

### C1. 没有 description 字段

**Spec 的 prompt 结构（§3.2 [B]）:** 直接注入 `task.description`

**实际:** 没有 description。模型需要从 train examples 中自行推断规则。

**影响:**
- prompt 中需要展示全部或部分 train examples（以 grid 文本形式）
- 部分 task 的 train 有 8+ 个 example，每个可能是 30×30 grid，全展示会导致 20k token 上限很快炸
- 需要 example 选择/截断策略

**建议 spec 修改方向:**
- 删除 `{description}` 占位符，改为 `{train_examples}` 
- 定义 train example 的展示格式和截断策略
- 或者考虑为每个 task 预生成一句话描述（用 LLM）

---

### C2. 输出格式要求不同

**Spec 的 [G] 模板:**
```
<notes>...</notes>
\`\`\`python
（完整程序）
\`\`\`
```

**实际需要:** notes 部分仍然适用，但代码块的期望从"读 stdin 写 stdout"变成"定义 `p` 函数/lambda"。

---

### C3. Prompt caching 策略

**Spec 说:** system + [B][C] 作为稳定前缀，命中 API 缓存

**实际:** 如果 [B] 是 train examples（每个 task 不同），那 cache 只在同一 task 的多轮间共享，跨 task 不共享。策略仍然是正确的，但收益变小了。

---

## D. 配置 & 模型（§5）

### D1. 模型配置的具体参数

**Spec 的 config.yaml 示例缺少:**
- `reasoning_effort` 参数（DeepSeek v4 需要 `extra_body={"thinking": {"type": "enabled"}}`）
- `max_tokens` / `max_output_tokens` 上限
- Anthropic 的 `cache_control` 显式标记方式

**建议:** 补充完整可运行的模型配置示例

---

### D2. API 重试策略

**Spec 说:** 指数退避 5 次（1/2/4/8/16s），连续 10 次 api_error 则失败

**实际经验:** 
- DeepSeek 有时返回空 content（reasoning 模式不一定有 content），不算 error 但 parse 会失败
- 需要区分 retryable error（429/503/connection reset）和 non-retryable error（401/403/400）

**建议:** 明确哪些 HTTP 状态码可重试，哪些直接放弃

---

## E. 目录结构与路径（§0、§7）

### E1. tasks/ 目录位置

**Spec 说:** `tasks/` 在项目根目录

**实际:** 任务是 `code-golf/google-code-golf-2025/task*.json`，约 500MB

**选项:**
- 在 bench/ 内建 symlink 指向实际位置
- 通过 config.yaml 配置任务路径

---

### E2. 任务还有额外文件

每个 task 在 `deepseek-v4-pro-baseline/task*/` 下还有:
- `gen.py` — 数据生成器（核心推理材料）
- `verify.py` — 官方验证脚本
- `common.py` — 共享工具函数
- `data.json` — 可能是子集数据

**问题:** gen.py 是否应该注入 prompt？（现有 agent.md 反复强调要先读 gen.py）

---

## F. 缺失的规范

以下内容 spec 没有覆盖，但在实际实现中需要决策:

### F1. 模型输出解析失败的处理

**Spec 说:** parse_error 计入轮数

**但没说明:**
- 如果模型输出的代码有语法错误怎么办？
- 如果定义的函数名不是 `p` 怎么办？
- 如果代码可以 import 但调用 `p(input)` 抛异常怎么办？

**建议:** 区分 `parse_error`（提不出代码）vs `runtime_error`（代码跑不了）vs `wrong_output`（跑了但结果不对）

---

### F2. 大 task 的判定性能

部分 task 有 ~50 个 test cases，每个可能是 30×30 grid。对所有 candidate 跑全量判定会非常慢。

**建议:** spec 已经提到短路策略和执行并发，但需要具体参数（先跑几个？并发几路？）

---

### F3. 轮数 vs 正确性优先

Spec 规定 30 轮 x 3 seeds。但如果模型前 10 轮全是 parse_error 或 runtime_error，后面 20 轮有价值吗？

**建议:** 考虑 early stopping 条件（连续 N 轮无进步？无正确解即停止？）

---

## G. 汇总：需要你决策的关键问题

| # | 问题 | 优先级 |
|---|------|--------|
| 1 | 采用 function-call `p(input)` 模式还是改成 stdin/stdout？ | 🔴 阻塞 |
| 2 | 没有 description 的情况下，prompt 如何展示题目信息？ | 🔴 阻塞 |
| 3 | 判定逻辑：numpy.array_equal 还是文本严格匹配？ | 🔴 阻塞 |
| 4 | train/test/arc-gen 三个 split 各自怎么用？ | 🔴 阻塞 |
| 5 | gen.py 要不要注入 prompt？ | 🟡 重要 |
| 6 | macOS 资源限制的 fallback 策略？ | 🟡 重要 |
| 7 | 字节数计算：文件大小 or len(encode())？ | 🟢 细节 |
| 8 | 大 task 的判定并发度和截断参数？ | 🟢 细节 |
| 9 | parse_error / runtime_error / wrong 的细分处理？ | 🟢 细节 |
| 10 | early stopping 条件？ | 🟢 细节 |
