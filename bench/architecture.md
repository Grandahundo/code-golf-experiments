# 架构概览

```mermaid
flowchart TB
    subgraph 输入["📥 输入"]
        T[400 道题目<br/>task*.json<br/>train + test + arc-gen]
        G[生成器 gen.py<br/>仅 task001-010]
        C[config.yaml<br/>模型/并发/预算]
    end

    subgraph 核心["🔄 Agentic Loop — 每题 30 轮"]
        P[1. 拼 Prompt<br/>system + gen.py<br/>+ 样例 + 状态 + 笔记]
        L[2. 调 LLM<br/>DeepSeek / GLM / Qwen<br/>重试 5 次退避]
        X[3. 解析回复<br/>取最后一个 ```python<br/>+ &lt;notes&gt; 笔记]
        J[4. 判分<br/>子进程沙箱 → 逐用例<br/>normalize → 比对]
        R[5. 记录<br/>trajectory.jsonl<br/>best.py / meta.json]

        P --> L --> X --> J --> R
        R -->|下一轮| P
    end

    subgraph 输出["📤 输出"]
        O1[runs/模型/题目/seed{n}/<br/>trajectory + best.py + meta]
        O2[scoring.py 聚合<br/>record_bytes / your_bytes]
        O3[leaderboard.csv<br/>per_task.csv]
    end

    T & G --> P
    C --> L
    R --> O1 --> O2 --> O3
```

```mermaid
flowchart LR
    subgraph 判分细节["⚙️ executor.py 判分细节"]
        A[代码 compile 检查] --> B{syntax ok?}
        B -->|no| E1[syntax_error]
        B -->|yes| C[子进程 judge_wrapper.py]
        C --> D{import 成功?}
        D -->|超时| E2[timeout]
        D -->|无 p| E3[no_p]
        D -->|异常| E4[crash]
        D -->|yes| F[逐用例 signal.alarm 2s]
        F --> G{全部通过?}
        G -->|yes| H[correct ✅]
        G -->|no| I{wrong / crash?}
        I -->|输出不对| J[wrong ✗]
        I -->|超时/异常| K[crash 💥]
    end
```

```mermaid
flowchart LR
    subgraph 调度["🚀 runner.py 调度"]
        M[作业矩阵<br/>task × model × seed] --> N[逐个检查 meta.json<br/>已完成则跳过]
        N --> O[每模型独立信号量<br/>默认并发 8]
        O --> P[asyncio 并发执行]
        P --> Q[每 60s 打印进度<br/>Ctrl-C 优雅退出]
    end
```

```mermaid
flowchart LR
    subgraph 数据流["📊 一Round数据流"]
        D1[task.json] --> D2[TaskBundle] --> D3[build_prompt] --> D4[LLM API] --> D5[parse_reply] --> D6[judge] --> D7[trajectory.jsonl]
    end
```
