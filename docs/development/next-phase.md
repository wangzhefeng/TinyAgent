> 所属：[TinyAgent Docs](../README.md) › 开发

# 下一阶段方向评审

状态：**方向 D（nami-agent 功能补齐）已完成（2026-10-31），下一主方向待评审**。候选 B 的评审清单见第 3 节。

## 1. 已完成：方向 C（评测补齐）

- learning / routine 两域契约、fixtures、三域校验与真实模型运行器（`evals/run_scenarios.py`）已落地。
- 真实模型验收 8 任务 × 3 轮全过（24/24，`glm-5.3-flash`）；基线与运行方式见[评测规范](../evaluation/scenarios.md)。
- 方向取舍与被否决理由见[设计决策 D6](../architecture/decisions.md)。

## 2. 已完成：方向 D（nami-agent 功能补齐）

七项全部落地，各自独立提交：D-1 `fetch_url`、D-2 审批体验（真实参数渲染/拒绝原因/一直允许）、D-3 AGENTS.md 常驻与技能防清理、D-4 计划模式、D-5 MCP 接入 CLI、D-6 `schedule daemon`、D-7 单层子 Agent。聊天渠道经评审不接入，与 D1 边界一致。设计取舍见[设计决策 D4/D5/D7](../architecture/decisions.md)。

验收：`uv run pytest tests -q`（64 通过）、`uv run ruff check .`、`uv run python scripts/check_docs.py`、`uv run python -m evals.run_eval` 全绿。

## 3. 候选主方向：B（日常影子运行）

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
