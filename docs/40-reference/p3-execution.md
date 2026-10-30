> 所属：[TinyAgent Docs](../README.md) › [参考资料](index.md)

# P3：记忆、检索与 Skills 学习循环

状态：**已完成（2026-10-30）**。本阶段实现 Hermes 式个人学习循环的受限版本：主会话自动记忆并审计，Skills 先草稿后审核，历史检索和压缩均不破坏原始事件。

## 1. 已交付

- `USER.md` / `MEMORY.md`：容量限制、增删改、原子写入和会话开始冻结快照；新写入不修改当前会话快照。
- `remember`：仅保存稳定偏好、环境约定和重复经验；主会话自动写入并追加 `memory_write` 审计，定时/子任务拒绝写入。
- FTS5：事件追加时同事务索引，旧事件自动回填；`search_sessions` 支持同一会话多词全部命中，返回 event 定位与短片段。
- Skills：`skills/` 正式只读与 `skill-drafts/` 隔离；`create_skill_draft` 需要审批，未审核不可加载，人工 `approve_draft` 后按需加载。
- ContextView：组合冻结记忆、Skills 目录和按需内容；达到硬阈值先尝试保存稳定记忆，再在完整 user 回合边界生成摘要。
- `context_artifacts`：保存摘要来源和派生内容；单长回合不强行摘要，原始事件与 tool call 配对保持不变。

## 2. 代码入口

| 模块 | 职责 |
|---|---|
| `src/tinyagent/memory/` | 记忆文件、容量与冻结快照 |
| `src/tinyagent/skills/` | Skills 目录、草稿与人工审核 |
| `src/tinyagent/tools/learning.py` | remember、search_sessions、load_skill、create_skill_draft |
| `runtime/store.py` | FTS5、会话状态与 context_artifacts |
| `agent/context.py` | 记忆/Skills 提示、清理与摘要视图 |
| `runtime/runtime.py` | 学习工具、审计、压缩前记忆与摘要 |

## 3. 验证结果

- 新增 8 个 P3 用例，项目总计 **64 项测试通过**。
- 真实模型保存两项用户偏好；新会话冻结快照正确生效，历史检索返回对应 session/event 证据。
- 技能草稿未审核不可加载；人工审核后，`cited-research` 成功指导包含 claims/evidence/unresolved/summary 的带引用报告。
- `uv run pytest tests -q`、`uv run ruff check .`、`uv run python scripts/check_docs.py` 全部通过。

## 4. 当前边界

- 记忆自动写入仅用于主会话稳定事实；一次性进展、定时任务和子任务不能自动写长期记忆。
- Skills 不提供无审核自我修改；没有技能市场、热加载或自动执行草稿。
- 当前仍是单用户、单进程；无聊天渠道、JSON-RPC、Graph 或 Agent 团队。
- 例行 Scheduler、有限预授权和无人值守在 P4 实现。

下一阶段 P4：Scheduler、独立会话、有限预授权、心跳与本地投递。

## 相关

- [重构总纲](refactor-plan-product.md) ｜ [P2 执行文档](p2-execution.md) ｜ [ADR-0009](../10-framework/adr/0009-event-store-sqlite.md) ｜ [ADR-0010](../10-framework/adr/0010-context-view.md) ｜ [ADR-0011](../10-framework/adr/0011-approval-execution.md)
