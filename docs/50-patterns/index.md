> 所属：[TinyAgent Docs](../README.md) › [模式实验室](index.md)

# L4：架构模式实验室

## 定位

同一批任务在不同架构模式下的对照实现与小结，用自研框架逐个实现；部分模式以 Copilot 的真实任务为实验对象，避免玩具化。

## 模式清单（六模式已实现，2026-10-25）

统一入口（顺序跑通并打印 ✅/❌ 结果）：

```bash
python -m learn.level4_patterns.run_all
```

| 模式 | 实现 | 要点 |
|---|---|---|
| Prompt Chaining | `chaining.py` | 提取 → 润色两段链；每步一个专注子任务 |
| Routing | `routing_pattern.py` | 意图分类分发四条链（框架版，L0 的进阶） |
| Self-Correction | `self_correction.py` | 生成 + 校验器 + 失败带反馈重试（JSON 合法性校验） |
| Evaluator-Optimizer | `evaluator_optimizer.py` | 打分者给 1-10 分与建议，优化者改写，观察分数轨迹 |
| Supervisor | `supervisor.py` | analyst → reporter 顺序编排两个专家（应用层编排范式） |
| Swarm/Handoffs | `swarm_handoff.py` | 框架 `Swarm` 对等移交（ADR-0004） |

已由其他层覆盖、此处不重复实现的模式：

- **ReAct / Plan-and-Execute / Reflection**：L1 手写版 + L2 框架版（`learn/level1_from_scratch/`、`level2_own_framework/`）。

## 后续（M5）

- 用 `evals/` 数据集对关键模式做量化对比（延迟 / 成本 / 稳定性）。

## 相关

- [20-framework](../20-framework/index.md)（Swarm/handoff 实现）｜ [70-evals](../70-evals/index.md)
