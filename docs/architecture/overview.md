> 所属：[TinyAgent Docs](../README.md) › 架构

# 当前架构

## 1. 目标与分层

TinyAgent 是 Python 自托管、单用户个人 Agent，通过 CLI 执行任务、操作受限工作区、保留记忆与 Skills，并运行定时任务。

```text
CLI
  ↓
Personal Runtime：Conversation / Run / Approval / Scheduler
  ↓
Agent：原生工具调用 / ContextView / Event
  ↓
Workspace Tools / Memory / Skills / Execution Backend
  ↓
SQLite：事件、会话、任务、审批、FTS5；JSONL 仅导出
```

核心不导入 CLI；安全规则由代码执行，不依赖模型自觉。会话回滚不代表文件、命令或外部副作用已回滚。

## 2. 模块职责

```text
src/tinyagent/
├── api.py        # 稳定公共 API
├── agent/        # Run/Event、ContextView 与摘要
├── core/         # 模型、消息与工具协议
├── runtime/      # SQLite、执行、恢复、审批与 Scheduler
├── tools/        # 工作区、学习和调度工具
├── execution/    # 本地、Seatbelt、bubblewrap 后端
├── memory/       # USER/MEMORY 与冻结快照
├── skills/       # Skills 目录、草稿与人工审核
├── channels/     # CLI 渠道
├── ext/          # 可选 MCP 工具源
└── cli.py        # 应用入口
```

| 模块 | 当前职责 |
|---|---|
| `agent/` | 原始事件到模型视图的转换、截断、清理与配对检查 |
| `runtime/` | Run 生命周期、幂等、恢复、usage、审批和定时执行 |
| `tools/` | 文件、检索、记忆、Skills 与调度工具 |
| `execution/` | 命令白名单、超时、输出限制和沙箱降级 |
| `memory/`、`skills/` | 可审查的长期记忆与按需加载能力 |
| `channels/`、`cli.py` | 单用户命令行交互 |

## 3. 公共 API

稳定入口为 `from tinyagent import ...`：

- 上下文与记录：`ContextBuilder`、`ContextView`、`EventRecord`、`RunRecord`。
- 模型与工具：`ChatModel`、`OpenAIChatModel`、`Tool`、`ToolRegistry`、`tool` 及消息类型。
- 运行时：`PersonalRuntime`、`SQLiteStore`、`Scheduler`、`LocalOutbox` 与取消异常。

## 4. 当前边界

- 单进程、单用户、单写入者；不同会话可独立运行，同一会话串行执行。
- 只有 CLI 和本地 JSONL 投递，没有 HTTP 服务、Web UI、JSON-RPC 或远程审批。
- 没有 Graph、多 Agent、多租户、分布式队列或多节点写入。
- 没有独立 plan 模式、自动备份恢复或其他格式的自动会话导入。

## 5. 架构决策

核心设计的选择原因、替代方案与边界统一见[设计决策](decisions.md)。

## 相关

- [使用指南](../usage/guide.md) ｜ [开发指南](../development/contributing.md)
