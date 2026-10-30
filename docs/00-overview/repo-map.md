> 所属：[TinyAgent Docs](../README.md) › [概览](index.md)

# 代码 → 文档映射

修改代码时，按下表同步对应文档。

| 代码区域 | 文档 |
|---|---|
| `src/tinyagent/api.py` | [个人 Agent 框架与 v1.0 公共 API](../10-framework/index.md) |
| `src/tinyagent/agent/` | [ADR-0010](../10-framework/adr/0010-context-view.md)、各阶段执行文档 |
| `src/tinyagent/runtime/` | [ADR-0008](../10-framework/adr/0008-runtime-json-rpc.md)、[ADR-0009](../10-framework/adr/0009-event-store-sqlite.md) |
| `src/tinyagent/tools/` | [ADR-0011](../10-framework/adr/0011-approval-execution.md)、[environment](environment.md) |
| `src/tinyagent/execution/` | [ADR-0011](../10-framework/adr/0011-approval-execution.md)、[P2](../40-reference/p2-execution.md) |
| `src/tinyagent/memory/` | [ADR-0009](../10-framework/adr/0009-event-store-sqlite.md)、[P3](../40-reference/p3-execution.md) |
| `src/tinyagent/skills/` | [P3](../40-reference/p3-execution.md) |
| `src/tinyagent/runtime/scheduler.py`、`tools/scheduler.py` | [ADR-0008](../10-framework/adr/0008-runtime-json-rpc.md)、[P4](../40-reference/p4-execution.md) |
| `src/tinyagent/channels/`、`cli.py` | 根 README、各阶段执行文档 |
| `evals/` | [application-scenarios](../20-evals/application-scenarios.md)、[20-evals](../20-evals/index.md) |
| `tests/` | [testing](../30-development/testing.md) |
| `results/`、`logs/` | [outputs](../30-development/outputs.md) |
| `scripts/` | [environment](environment.md)、[AGENTS](../../AGENTS.md) |
| 文档结构本身 | [docs-maintenance](../30-development/docs-maintenance.md) |

## 规则

- 目录新增、移动或删除时，同步根 README、[architecture](architecture.md) 与本页。
- 阶段实现与验收记录放在 `docs/40-reference/`；清理动作同时记录到 [cleanup-log](../30-development/cleanup-log.md)。
- 历史重构方案见 [refactor-plan-product](../40-reference/refactor-plan-product.md) 与 [product-refactor-migration](../40-reference/product-refactor-migration.md)。
