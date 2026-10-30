> 所属：[TinyAgent Docs](../README.md) › [自研框架](index.md)

# 个人 Agent 框架

## 定位

Python 自托管、单用户个人 Agent：小型 Agent 核心 + 可选 Personal Runtime + 工作区与学习能力。框架服务于个人应用，不追求通用编排平台。

## 设计要点

- **小内核**：模型请求工具，代码执行并回填结果；原生工具调用优先。
- **无损事实源**：SQLite 保存不可变事件，ContextView 只决定模型看到什么。
- **确定性安全**：路径、审批、沙箱、预授权和 Skills 审核都在代码层，不依赖模型自觉。
- **学习循环**：主会话自动记忆并审计，历史用 FTS5 检索，Skills 先草稿后审核。
- **例行自动化**：定时任务使用独立会话和有限预授权，心跳无事不投递。

## 当前实现（P1–P4）

| 模块 | 职责 |
|---|---|
| `agent/` | Run/Event、ContextView、摘要与配对检查 |
| `runtime/` | SQLite、执行、恢复、审批、usage 与 Scheduler |
| `tools/` | 工作区、学习、调度工具 |
| `execution/` | 本地、Seatbelt、bubblewrap 后端 |
| `memory/` | USER/MEMORY、容量与冻结快照 |
| `skills/` | Skills 草稿、审核与按需加载 |
| `channels/`、`cli.py` | 单用户 CLI |

验证：38 项测试全绿；真实模型完成只读调查、精确编辑、带引用调研、跨会话记忆和心跳投递。

## v1.0 公共 API

稳定入口统一为 `from tinyagent import ...`，仅暴露三组能力：

- 上下文与记录：`ContextBuilder`、`ContextView`、`EventRecord`、`RunRecord`。
- 模型与工具：`ChatModel`、`OpenAIChatModel`、`Tool`、`ToolRegistry`、`tool` 及相关消息类型。
- 个人运行时：`PersonalRuntime`、`SQLiteStore`、`Scheduler`、`LocalOutbox` 与取消异常。

旧 `TinyAgent`、Agent 变体、Swarm、双 codec、旧 Memory/Session/Tracer 不再导出；历史实现归档在私有 `TinyAgent-lab` 的 `legacy-v0/`。

## ADR

- [ADR-0001 内核与六协议](adr/0001-agent-loop-and-protocols.md)
- [ADR-0002 双 codec](adr/0002-call-codec.md)
- [ADR-0003 session 与 tracing](adr/0003-session-and-tracing.md)
- [ADR-0004 handoff 与 Swarm](adr/0004-handoff-and-swarm.md)
- [ADR-0005 MCP 工具源](adr/0005-mcp-tool-source.md)
- [ADR-0006 Graph Runtime 提案](adr/0006-graph-runtime-proposal.md)（暂缓）
- [ADR-0007 长期记忆](adr/0007-long-term-memory.md)
- [ADR-0008 Personal Runtime](adr/0008-runtime-json-rpc.md)（P4 已实现；JSON-RPC 后置）
- [ADR-0009 SQLite、FTS5 与记忆存储](adr/0009-event-store-sqlite.md)（P4 已实现）
- [ADR-0010 ContextView 与学习上下文](adr/0010-context-view.md)（P3 已实现）
- [ADR-0011 审批与执行安全](adr/0011-approval-execution.md)（P4 已实现）

## 相关

- [个人 Agent 重构方案](../40-reference/refactor-plan-product.md)
- [个人 Agent 评测](../20-evals/index.md)
