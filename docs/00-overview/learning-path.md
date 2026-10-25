> 所属：[TinyAgent Docs](../README.md) › [概览](index.md)

# 学习地图与里程碑

## 学习路径 L0–L6

| 层级 | 主题 | 产出 | 状态 |
|---|---|---|---|
| L0 | LLM API 基础：chat、流式、结构化输出、链式/路由 | `learn/level0_llm_basics/` 可运行示例 | **M1 完成**（routing/共享客户端） |
| L1 | 从零手写：ReAct / Plan-Execute / Reflection 最小实现 | `learn/level1_from_scratch/` 三范式 + API 化改造 | **M1 完成**（三范式 + Copilot C0 实跑通过） |
| L2 | 自研框架：用 tinyagent 重写 L1，对标源码笔记 | `packages/tinyagent-core` v0.x + `learn/level2_own_framework/` | **v0.1 已落地**（M2，L2 对照 demo 通过） |
| L3 | LangGraph：agents-from-scratch 邮件助手课程 | `learn/level3_langgraph/` 课程项目（HITL/记忆/多智能体） | **M3 完成**（三 part 实跑通过） |
| L4 | 模式实验室：路由/链式/反思/自纠错/…对照实现 | `learn/level4_patterns/` | **M4 完成**（六模式实跑） |
| L5 | 生态与协议：MCP、ADK、框架横评、本地部署 | `learn/level5_ecosystem/` | **M4 完成**（MCP 双向；ADK 说明就位） |
| L6 | 评测与观测：evals、tracing、对比实验 | `learn/level6_evals/` + `evals/` | 规划（M5） |

## 工程里程碑 M0–M5

| 里程碑 | 内容 | 验收 |
|---|---|---|
| M0 结构迁移 | 目录骨架、git mv、删除项、README 索引化、docs 域页落位、workspace 化 | check_docs OK；抽样运行每域一个入口 |
| M1 L0+L1 | 手写三范式 API 化；Copilot C0 只读工具 | 无本地模型可跑通三范式 |
| M2 框架 v0.1 | 六协议内核 + 单测 + examples | 独立可安装，单测覆盖 loop/codec/session |
| M3 LangGraph | 邮件助手课程 + Copilot HITL/断点 | 课程项目全程跑通 |
| M4 模式+生态 | patterns 实验室 + MCP/ADK + Copilot 多智能体 | 框架可挂载自建 MCP server |
| M5 评测收尾 | evals + 三版本 Copilot 对照 + Survey Agent | 同一评测集出可对比数据 |

详细执行方案见[重构方案（评审稿）](../90-reference/refactor-plan-2026-10.md)。
