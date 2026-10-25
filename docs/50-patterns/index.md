> 所属：[TinyAgent Docs](../README.md) › [模式实验室](index.md)

# L4：架构模式实验室

## 定位

同一批任务在不同架构模式下的对照实现与小结，参考 [all-agentic-architectures](https://github.com/FareedKhan-dev/all-agentic-architectures) 的模式清单，用自研框架逐个实现。

## 模式清单（规划）

| 模式 | 一句话 | 优先级 |
|---|---|---|
| Prompt Chaining | 串行流水线，每步一个专注子任务 | 高（L0 已有雏形） |
| Routing | 按输入类型分流到不同处理链 | 高 |
| ReAct | 思考-行动-观察循环 | 高（L1 已有） |
| Plan-and-Execute | 先整体规划再逐步执行 | 高（L1 已有） |
| Reflection | 生成-批评-修订循环 | 高（L1 已有） |
| Self-correction / Retry | 执行失败自纠错重试 | 中 |
| Multi-agent Supervisor | 中央调度 + 专家执行 | 中（C3 前置） |
| Swarm / Handoffs | 同伴间控制权移交 | 中（框架 v0.3） |
| Evaluator-Optimizer | 打分者与优化者对抗迭代 | 低 |

## 规划（M4）

1. 每模式：最小实现 + 适用场景 + 代价（延迟/成本/复杂度）笔记，落于 `learn/level4_patterns/`。
2. 用 Copilot 的真实任务（配置生成、指标对比）作为部分模式的实验对象，避免玩具化。

## 相关

- [10-scratch](../10-scratch/index.md)：三种范式的手写版
- [70-evals](../70-evals/index.md)：模式间的量化对比
