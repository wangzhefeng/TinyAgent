# ADR-0008：Personal Runtime 与任务生命周期

> 所属：[TinyAgent Docs](../../README.md) › [自研框架](../index.md) › ADR

日期：2026-10-30 ｜ 状态：P4 已实现 Runtime 与 Scheduler；JSON-RPC 后置

## 背景

个人 Agent 需要统一管理 CLI 任务、审批、恢复和定时任务，但首期为单进程、单用户应用，不需要把 Runtime 独立成服务平台。Runtime 参考 Pi Durable 的可选分层，调度参考 Hermes 的隔离任务会话。

## 决策

### 1. Run 状态机

```text
queued → running → completed
           │  ├────→ failed
           │  └────→ cancelled
           ├─→ waiting_approval → running
           └─→ waiting_approval → cancelled
```

- 状态迁移与事件追加在同一 SQLite 事务中提交；非法迁移返回冲突错误。
- 取消是协作式的，在模型调用和工具执行边界生效；强制终止不等于外部副作用已撤销。
- 进程恢复不盲目重放结果未知的工具；未知副作用标记失败并要求人工核查。
- 重试失败 Run 默认创建带 `retry_of` 的新 Run，不改写历史。

### 2. 核心数据与分支预留

- Run：`id / session_id / kind / status / input / output / usage / error / created_at / updated_at / version`；kind 为 interactive/scheduled/subtask。
- Event：`event_id / parent_event_id / session_id / run_id / seq / type / data / ts / schema_version`；`seq` 在 Run 内递增。
- Session 记录当前 leaf；首期只线性执行，`parent_event_id` 为未来分支保留，不实现分支 UI。
- Usage 分别记录输入、输出 token、模型/工具调用数和延迟；缺失值记 unknown，不记零。

### 3. 首期进程内接口

CLI 直接调用 Runtime，不经过网络或 JSON-RPC：

| 接口 | 语义 |
|---|---|
| `create_run` | 创建 interactive/scheduled Run，接受幂等键 |
| `get_run` | 查询状态、usage、error 和最后事件序号 |
| `cancel_run` | 请求协作式取消，重复调用返回当前状态 |
| `resume_run` | 恢复可安全恢复的 Run，不重放未知副作用 |
| `respond_approval` | 按 approval_id 批准或拒绝，可附原因 |
| `subscribe_events` | 按序号订阅和重放事件，慢消费者可重新订阅 |

相同幂等键和请求返回原 Run；相同键不同请求返回冲突。审批重复且决定一致时幂等，冲突决定返回错误。

### 4. Scheduler

- scheduled Run 使用全新隔离会话，不读取互动会话的“一直允许”状态。
- 仅放行创建任务时明确预授权的工具；定时任务不能再创建任务，也不能自动写 Skills。
- 先持久化下次执行时间再运行；停机错过默认不补跑，避免重启后连续执行。
- 心跳无结果时只记录，不投递；每次执行仍记录模型/工具调用与成本。
- 首期为 CLI/本地投递；聊天渠道只实现相同的输入、输出和审批接口，后续再接入。

### 5. 可选 JSON-RPC

只有出现第二个真实客户端时才评审 stdio JSON-RPC；届时复用进程内接口、NDJSON、请求 ID 和事件通知，不让协议绕过 Runtime 的幂等与安全约束。HTTP、远程认证和多 worker 继续后置。

## 后果与验证

Runtime 支撑个人任务而不成为独立平台。测试覆盖状态迁移、重复创建、冲突审批、取消恢复、慢消费者、隔离任务、错过不补跑、任务不能再建任务和未知副作用。

## 相关

- [ADR-0009 SQLite 与 FTS5](0009-event-store-sqlite.md) ｜ [个人 Agent 重构方案](../../40-reference/refactor-plan-product.md)
