> 所属：[TinyAgent Docs](../README.md) › [概览](index.md)

# 学习地图与里程碑

## 学习路径 L0–L6

| 层级 | 主题 | 产出 | 状态 |
|---|---|---|---|
| L0 | LLM API 基础：chat、流式、结构化输出、链式/路由 | `learn/level0_llm_basics/` 可运行示例 | 迁移期（源自 `src/TinyAgent/`） |
| L1 | 从零手写：ReAct / Plan-Execute / Reflection 最小实现 | `learn/level1_from_scratch/` 三范式 + API 化改造 | 迁移期（M1 改造） |
| L2 | 自研框架：用 tinyagent 重写 L1，对标源码笔记 | `packages/tinyagent-core` v0.x + `learn/level2_own_framework/` | 规划（M2） |
| L3 | LangGraph：agents-from-scratch 邮件助手课程 | `learn/level3_langgraph/` 课程项目（HITL/记忆/多智能体） | 规划（M3） |
| L4 | 模式实验室：路由/链式/反思/自纠错/…对照实现 | `learn/level4_patterns/` | 规划（M4） |
| L5 | 生态与协议：MCP、ADK、框架横评、本地部署 | `learn/level5_ecosystem/` | 迁移期（mcp_dev / adk_dev / framework / local_server） |
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
