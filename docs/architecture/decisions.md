> 所属：[TinyAgent Docs](../README.md) › [架构](overview.md)

# 架构设计决策

本文记录当前核心设计的原因、选择与边界。系统结构和模块说明见[架构概览](overview.md)。

## D1：采用进程内 Personal Runtime

**背景**：单用户 Agent 需要统一管理任务、审批、恢复和定时执行，但当前没有多客户端或多节点需求。

**决策**：

- CLI 直接调用 `PersonalRuntime`，不经过 HTTP 或 JSON-RPC。
- Run 保存状态、输入输出、usage 和错误；Event 只追加，Session 记录当前 leaf。
- 支持幂等创建、协作式取消和原 Run 恢复；不盲目重放结果未知的工具。
- Scheduler 使用独立会话、有限预授权和本地心跳投递。

**边界**：当前没有事件订阅、远程审批、`retry_of` 或自动重试 Run。出现第二个真实客户端后再评审服务接口。

## D2：SQLite 保存事实，文本保存稳定记忆

**背景**：任务状态和会话检索需要事务与全文索引，长期偏好则需要可审查、可编辑的表示。

**决策**：

- SQLite 保存 runs、events、sessions、approvals、idempotency、context artifacts 和 scheduled tasks。
- `session_fts` 与原始事件在同一事务中更新，检索返回 session/event 定位和短片段。
- `USER.md` 保存稳定偏好，`MEMORY.md` 保存环境约定与重复经验，会话开始冻结快照。
- 数据库、记忆和 Skills 位于 workspace 外；Skills 草稿审核后才可加载。

**边界**：当前是单写入者，不支持多节点写入；自动备份恢复和其他格式的会话导入尚未实现。

## D3：原始事件与 ContextView 分离

**背景**：完整历史需要长期保存，但模型上下文必须有限，压缩不能破坏事实或 tool call 配对。

**决策**：

- 每次模型调用前由 `ContextBuilder` 从事件生成视图，原始事件不变。
- 依次采用工具结果头尾截断、旧结果清理、压缩前记忆和完整回合摘要；旧结果清理跳过 `[skill]` 技能正文，截断行为不变。
- 常驻内容仅包括系统约定、工作区 `AGENTS.md`（截断上限）、当前任务、冻结记忆和 Skills 目录，其他内容按需加载。
- 默认软/硬阈值为 16000/24000 tokens；缺少 API usage 时按约 4 字符一个 token 估算并标记。

**边界**：按模型窗口自动计算阈值和模型 tokenizer 适配尚未实现；单长回合不强行摘要。

## D4：安全边界由代码确定性执行

**背景**：文件、命令、长期记忆和无人值守任务都有真实副作用，不能依赖模型遵守提示词。

**决策**：

- 默认只读；`--writable` 只开放能力，写入和 shell 仍需审批。
- 路径检查覆盖绝对路径、`..` 和符号链接；shell 使用白名单、固定目录、超时和输出上限。
- 审批提示按工具渲染真实参数；拒绝可附原因回传模型；仅 `write_file` 支持「本次运行一直允许」，其余工具逐次确认。
- `/plan` 进入计划模式：仅只读调查与 `update_plan` 可用，其余操作由代码直接拒绝；`submit_plan` 展示完整计划并经审批后退出，旧版计划在上下文中折叠为一行。
- macOS Seatbelt、Linux bubblewrap 优先；不可用时逐条确认，无人值守拒绝。
- 定时任务只放行明确预授权操作，shell 不可预授权；记忆写入有审计，Skills 必须人工审核。
- `fetch_url` 仅允许 http/https，限时并限制读取与输出；逐次审批，不可预授权，无人值守运行默认拒绝。

**边界**：本地降级没有硬隔离；远程渠道安全策略尚未实现。

## D5：MCP 是可选工具源

**背景**：外部 MCP server 可以扩展工具来源，但不应增加核心依赖或绕过统一审批。

**决策**：

- `MCPToolSource` 通过 stdio 连接 server，将工具 schema 映射为 `ToolSpec`。
- CLI 启动时读取 state 目录旁 `mcp.json`，以 `mcp__服务器__工具` 名注册进统一审批路径；仅配置 `safe_tools` 点名的工具计入只读名单。
- 依赖放入 `tinyagent[mcp]` extra；连接由上下文管理器显式关闭，描述与结果视为不可信输入。

**边界**：当前只支持 stdio；SSE 和 streamable HTTP 待真实需求出现后评审。

## D6：评测先行，影子运行其次，服务化最后

**背景**：v1.0.0 后有三个候选主方向：A 本地服务、B 日常影子运行、C 评测补齐。B 的成本与质量报告需要评分器与真实模型基线；A 与 D1 的"第二个真实客户端"边界冲突。

**决策**：

- 每次只选一个主方向；先做 C，补齐 learning/routine 应用级契约与真实模型运行器。
- C 完成并验收通过后评审 B；A 继续推迟到 D1 边界触发。

**边界**：C 已于 2026-10-31 完成并验收（8 任务 × 3 轮 24/24 通过，见[评测规范](../evaluation/scenarios.md)）。B 的评审清单见[下一阶段](../development/next-phase.md)。

## D7：单层子 Agent 用于隔离调查上下文

**背景**：大量只读调查会占满主会话上下文；nami-agent 教程验证了「独立上下文子 Agent + 只带回结论」的形态。此前多 Agent 列为默认非目标。

**决策**：

- 引入一层子 Agent：`delegate`（explore 只读 / worker 可写且逐次审批）与 `delegate_parallel`（≤3 并行只读）。
- 子 Agent 使用独立会话与上下文，深度限 1；派生、调度、计划、记忆工具不下发；审批继承父会话。
- 结论限长回传，中间过程不进入父会话；多层编排、Agent 间通信与并行写仍为非目标。

**边界**：子 Agent 深度限一层（子 Agent 工具集不含派生工具）；无人值守任务不允许派生子 Agent。

## 相关

- [架构概览](overview.md) ｜ [使用指南](../usage/guide.md) ｜ [下一阶段](../development/next-phase.md)
