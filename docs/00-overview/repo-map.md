> 所属：[TinyAgent Docs](../README.md) › [概览](index.md)

# 代码 → 文档映射

修改代码时，按下表找到应同步更新的文档（M0 结构迁移后按新目录组织，2026-10-25 重建）。

| 代码区域 | 文档 |
|---|---|
| `learn/level0_llm_basics/` | [10-scratch](../10-scratch/index.md) |
| `learn/level1_from_scratch/`（react / react_hello_agents / plan_execute / reflection / hello_agent_5min） | [10-scratch](../10-scratch/index.md) |
| `learn/level2_own_framework/` | [20-framework](../20-framework/index.md) |
| `packages/tinyagent-core/`（框架本体 + examples） | [20-framework](../20-framework/index.md) |
| `hello_agents/`（`src/`、`version.py`，M2 重构迁入后移除） | [20-framework](../20-framework/index.md) |
| `apps/experiment_copilot/`（doc_qa 及后续 Copilot 版本） | [30-copilot](../30-copilot/index.md) |
| `learn/level3_langgraph/`（M3 建立） | [40-langgraph](../40-langgraph/index.md) |
| `learn/level4_patterns/`（M4 建立） | [50-patterns](../50-patterns/index.md) |
| `learn/level5_ecosystem/`（mcp / adk / frameworks / deployment） | [60-ecosystem](../60-ecosystem/index.md) |
| `learn/level6_evals/`、`evals/`（M5 建立） | [70-evals](../70-evals/index.md) |
| `tests/` | [testing](../80-development/testing.md) |
| `dataset/`、`downloaded_models/`、`results/`、`logs/`（不入库） | [outputs](../80-development/outputs.md) |
| `utils/`、`scripts/` | [environment](environment.md)、[AGENTS](../../AGENTS.md) |
| 文档结构本身 | [docs-maintenance](../80-development/docs-maintenance.md) |

## 规则

- 表中"文档"指该域入口页；具体子页由域 `index.md` 二次导航。
- 结构迁移历史见[重构方案](../90-reference/refactor-plan-2026-10.md)。
