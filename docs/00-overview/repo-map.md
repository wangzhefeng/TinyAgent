> 所属：[TinyAgent Docs](../README.md) › [概览](index.md)

# 代码 → 文档映射

修改代码时，按下表找到应同步更新的文档（按当前目录组织；M0 结构迁移后本表按目标目录重建）。

| 代码区域 | 文档 |
|---|---|
| `src/TinyAgent/`（手写 ReAct Agent、prompt chaining、chat model） | [10-scratch](../10-scratch/index.md) |
| `hello_agents/src/`（框架复刻实现） | [20-framework](../20-framework/index.md) |
| `hello_agents/test/agent_mode/`（ReAct / PlanAndSolve / Reflection） | [10-scratch](../10-scratch/index.md) |
| `hello_agents/test/framework/`（langgraph / agentscope / autogen / camel） | [60-ecosystem](../60-ecosystem/index.md) |
| `hello_agents/test/local_server/`（ollama / vllm） | [60-ecosystem](../60-ecosystem/index.md) |
| `src/mcp_dev/` | [60-ecosystem](../60-ecosystem/index.md) |
| `src/adk_dev/` | [60-ecosystem](../60-ecosystem/index.md) |
| `src/qa_chain/`（RAG 问答，Copilot doc_qa 能力来源） | [30-copilot](../30-copilot/index.md) |
| `agent_usage/`（框架使用示例） | [20-framework](../20-framework/index.md) |
| `src/dify_dev/` | —（已决策删除，见[重构方案](../90-reference/refactor-plan-2026-10.md)映射 #12） |
| `utils/`、`scripts/` | [environment](environment.md)、[AGENTS](../../AGENTS.md) |
| 文档结构本身 | [docs-maintenance](../80-development/docs-maintenance.md) |

## 规则

- 表中"文档"指该域入口页；具体子页由域 `index.md` 二次导航。
- 结构迁移（M0）执行时必须同步重建本表，见[重构方案](../90-reference/refactor-plan-2026-10.md)。
