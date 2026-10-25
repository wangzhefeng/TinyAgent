> 所属：[TinyAgent Docs](../README.md) › [评测与观测](index.md)

# L6：评测与观测

## 定位

让"哪个版本更好"变成可回答的问题：评测方法、tracing、模式间与应用版本间的量化对比。

## 现状（M5 已完成，2026-10-25）

### 评测基建

- 评测集：`evals/datasets/`（5 题按场景分文件：`facts.jsonl` 取数事实、`caliber.jsonl` 口径综合；期望事实取自 tsproj_ml 真实产物）。
- Harness：`python -m evals.run_eval` 顺序跑 C0/C1/C3，按事实命中率 + 耗时 + 失败数打分，报告写 `results/evals/`（outputs 约定，不入库）。

### 三版本 Copilot 对照（2026-10-25 实测，15/15 零失败）

| 版本 | 架构 | 平均事实命中率 | 平均耗时(s) |
|---|---|---|---|
| C0 | 手写 ReAct + 只读工具 | **77%** | 58 |
| C1 | tinyagent 框架版 | 50% | 43（q1 仅 11.5s 满分） |
| C3 | planner/executor/analyst/reporter 多智能体 | 43% | 214 |

**发现（反直觉但有价值）**：

1. **取数事实题上，简单直接的工具循环最准最快**——C0/C1 的单 Agent 直查命中率高于多智能体；C3 的 planner 分解会引入检索路径分叉（q1/q2 被带偏），且延迟 3–5 倍。
2. **多智能体的价值在综合分析而非取数**：C3 在 q5（口径综合判断）拿到 2/3，长报告质量此前也验证过更优。
3. **评测集本身有歧义**：tsproj_ml 存在多个 naive identity（MAE 40.2/54.3 不等），子串打分偏严——记为评测改进项（题面指定具体 identity、或语义判分）。
4. **稳定性**：三版本 × 5 题 × 多轮工具调用全部零崩溃（错误回填机制生效）。

## 观测

- `JsonlTracer`（框架内置）事件流：`logs/tinyagent/traces/`；会话：`logs/tinyagent/sessions/`。
- LangSmith 后端对照未做（可选后续）。

## 相关

- [30-copilot](../30-copilot/index.md) ｜ [outputs 产物约定](../80-development/outputs.md)
