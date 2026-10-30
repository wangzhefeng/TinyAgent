# ADR-0009：SQLite、FTS5 与个人记忆存储

> 所属：[TinyAgent Docs](../../README.md) › [自研框架](../index.md) › ADR

日期：2026-10-30 ｜ 状态：P4 已实现 SQLite、FTS5、USER/MEMORY 与定时任务存储

## 背景

个人 Agent 同时需要事务化 Run/任务状态、可检索的完整会话和少量跨会话稳定记忆。采用 SQLite + FTS5 保存事实与检索，USER/MEMORY 采用可审查文本，JSONL 仅用于导出和迁移。

## 决策

### 1. SQLite 表与事件

| 表 | 关键内容 |
|---|---|
| `runs` | session/kind、状态、输入输出、usage、error、时间戳和 version |
| `events` | event_id、parent_event_id、session/run、seq、type、data、ts、schema_version；只追加 |
| `sessions` | 当前 leaf、来源、共享状态、version 和时间戳 |
| `approvals` | run/tool_call、动作快照、状态、决定者、原因和过期时间 |
| `idempotency_keys` | scope + key 唯一、request_hash、关联 Run 和创建时间 |
| `context_artifacts` | 摘要等派生物、来源事件范围、内容和创建时间 |
| `scheduled_tasks` | 时间规则、prompt、投递目标、预授权、下次执行、状态和版本 |

事件不得 UPDATE/DELETE；ContextView 和摘要只写派生记录。`session_fts` 索引用户/助手消息及必要的工具结果，与原始事件在同一事务中更新；检索返回 session/event 定位与短片段，不直接把整段历史塞入上下文。

### 2. 事务与并发

- 启用 foreign keys、WAL 和 busy timeout；使用 Python 标准库 `sqlite3` 与 SQLite FTS5，核心不新增数据库依赖。
- 首期只允许 Runtime 单写入者；同一会话串行执行，不同会话可读取和运行。
- “追加事件 + 更新 Run/审批/FTS/幂等记录”在一个事务内提交。
- 通过 event/run 主键、状态版本和幂等约束防止重复写入；数据库位于程序 state 目录，不在 workspace 内。

### 3. USER/MEMORY 与 Skills 文件

- `USER.md` 保存稳定用户偏好，`MEMORY.md` 保存长期环境约定和反复经验；均有可配置字符上限。
- 稳定记忆可在主会话自动写入，但必须产生审计事件，支持 replace/remove，禁止把一次性任务进展写成长期记忆。
- 会话开始时生成冻结快照；会话中新写入只落盘，避免持续修改 system prompt 前缀。
- 定时任务和子 Run 不得自动写长期记忆；待审核 Skills 位于独立目录，审核后才进入正式只读 Skills 目录。
- 文本文件、数据库和 Skills 都位于 Agent workspace 之外，使用原子替换防止半写入。

### 4. JSONL、迁移与备份

- JSONL 导出包含 schema 版本、Run 元数据和有序事件，不是在线真相源。
- 旧 messages/traces 映射为带 `legacy_source` 的新事件，保留原值并生成新主键；迁移前保留只读备份。
- 迁移后校验记录数、序列、工具调用配对、FTS 可检索性和抽样哈希；回滚不改写旧文件。
- 使用 SQLite backup API 或 WAL checkpoint 后备份；恢复时检查外键、事件连续性和 FTS 一致性，派生物可重建。

## 后果与验证

SQLite/FTS5 支撑单用户恢复和检索，文本记忆保持可审查；不支持多节点写入。测试覆盖事务回滚、事件不可变、FTS 一致、记忆上限/快照/增删改、自动写入审计、技能审核隔离、备份恢复和状态目录不可访问。

## 相关

- [ADR-0008 Personal Runtime](0008-runtime-json-rpc.md) ｜ [ADR-0010 ContextView](0010-context-view.md) ｜ [ADR-0011 安全](0011-approval-execution.md)
