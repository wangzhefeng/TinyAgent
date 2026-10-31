> 所属：[TinyAgent Docs](../README.md) › 开发

# 下一阶段方向评审

状态：**方向 D（nami-agent 功能补齐）已选定（2026-10-31），按项小步实施**；B 评审顺延至 D 主要项完成后。

## 1. 已完成：方向 C（评测补齐）

- learning / routine 两域契约、fixtures、三域校验与真实模型运行器（`evals/run_scenarios.py`）已落地。
- 真实模型验收 8 任务 × 3 轮全过（24/24，`glm-5.3-flash`）；基线与运行方式见[评测规范](../evaluation/scenarios.md)。
- 方向取舍与被否决理由见[设计决策 D6](../architecture/decisions.md)。

## 2. 执行中：方向 D（nami-agent 功能补齐）

范围决策（2026-10-31）：子 Agent 取完整版（D-7，决策记录见[设计决策 D7](../architecture/decisions.md)）；聊天渠道不接入，定时任务只做本地常驻调度（D-6）；其余五项按对 nami-agent 教程的对比结论逐项补齐。每项完成后按 AGENTS.md 第 5 节联动文档并小步提交。

完成定义：各项对应单测（及按需的 evals 场景）通过，`uv run pytest tests -q`、`uv run ruff check .`、`uv run python scripts/check_docs.py`、`uv run python -m evals.run_eval` 全绿。

### D-1 fetch_url 工具

- 改动：`src/tinyagent/tools/workspace.py` 新增 `fetch_url`（仅 http/https、限时、输出上限；CONFIRM 级每次确认），设计决策 D4 补网络抓取边界。
- 影响：工具清单与审批路径；调度预授权名单维持仅 `write_file`。
- 验证：单测 mock 网络响应，`uv run pytest tests -q`。

### D-2 审批体验

- 改动：`src/tinyagent/runtime/approvals.py` 按工具渲染真实参数（shell 命令、写入内容预览、计划全文、记忆原文），支持拒绝原因回传与「本会话一直允许」（仅 `write_file`）。
- 影响：审批交互与 `approvals` 表记录字段；`runtime.py` 审批事件随之扩展。
- 验证：单测覆盖参数渲染、拒绝原因、一直允许的生效范围。

### D-3 常驻说明与技能防清理

- 改动：`src/tinyagent/agent/context.py` 系统 prompt 纳入工作区 `AGENTS.md`（截断上限）；旧工具结果清理跳过 `[skill]` 前缀内容。
- 影响：`ContextBuilder` 输入与上下文清理行为；设计决策 D3 常驻内容描述更新。
- 验证：单测覆盖 AGENTS.md 进入 prompt、超阈值清理时技能结果保留。

### D-4 计划模式

- 改动：新增计划工具（`update_plan` / `submit_plan`）与会话计划状态；计划模式下由代码强制只读；`channels/cli.py` 增加 `/plan` 命令。
- 影响：审批路径（计划模式拒绝一切非只读操作）、会话状态存储；设计决策 D4 边界更新，使用指南补命令。
- 验证：单测覆盖进入/退出计划模式、越权拒绝、提交审批；evals 场景按需补充。

### D-5 MCP 接入 CLI

- 改动：`channels/cli.py` 读取 state 目录旁 `mcp.json`，注册 `mcp__服务器__工具`；只有配置点名的工具计入只读名单。
- 影响：registry 组装与审批路径；设计决策 D5 扩充，使用指南补配置格式。
- 验证：单测以示例 MCP server 验证注册与调用；未安装 `mcp` extra 时跳过。

### D-6 常驻调度

- 改动：新增 `tinyagent schedule daemon` 常驻命令，循环执行到期任务；投递仍走本地 `deliveries.jsonl`，不接聊天渠道。
- 影响：无新状态与权限面；使用指南补运行方式。
- 验证：单测以可控时钟验证到点触发与心跳免打扰；手动冒烟一轮。

### D-7 子 Agent（完整版）

- 改动：新增 `delegate`（explore 只读 / worker 可写且逐次审批）与 `delegate_parallel`（≤3 并行只读）；子 Agent 独立会话、深度限 1，派生/调度/计划/记忆工具不下发；结论限长回传，中间过程不进父会话。
- 影响：运行循环支持嵌套与会话内工具子集，审批继承父会话；设计决策 D7 已立项，架构概览补模块。
- 验证：单测覆盖只读边界、并行、深度限制、结论不进父上下文。

实施顺序：D-1 → D-2 → D-3 → D-4 → D-5 → D-6 → D-7。

## 3. 顺延：候选主方向 B（日常影子运行）

目标：验证 Agent 能否逐步承接真实个人任务。C 已补齐其技术前置：评分与用量管线、无人值守安全证据（预授权边界、投递恰好一次、记忆审计）、例行任务验收标准。

选定 B 前必须确认：

1. 任务来源：挑选并 sanitized 多少个真实日常任务，覆盖哪些能力面（只读调查 / 写入修复 / 例行监测）。
2. 运行周期与频率：影子运行多久（建议 ≥2 周），每日任务量与并发上限。
3. 成本上限与回滚：token / 费用上限与超限处置；记忆或 Skills 被污染时的恢复方式。
4. 人工评分方式：逐任务通过/失败加备注，还是分级评分；由谁评、多久评一次。
5. 定时任务迁移：是否把现有日常定时任务迁入影子运行；建议先从单个 heartbeat 试点。

确认后先在本文补 B 的任务拆解与完成定义，再修改代码。

## 4. 仍推迟：A（本地服务）

按[设计决策 D1](../architecture/decisions.md)，出现第二个真实客户端前不评审服务接口。

## 5. 默认非目标

不引入多租户、分布式队列、Graph、多层 Agent 编排、远程执行或公共通用框架兼容层；不默认替换现有日常主力工具。单层子 Agent 已纳入方向 D-7。

## 相关

- [使用指南](../usage/guide.md) ｜ [架构概览](../architecture/overview.md) ｜ [评测规范](../evaluation/scenarios.md)
