> 所属：[TinyAgent Docs](../README.md) › [参考资料](index.md)

# TinyAgent 个人 Agent 重构方案（设计评审稿）

状态：**方向与 D1–D19 已确认；P0–P5 全部完成（2026-10-30）**。本版取代此前“通用框架 + Workspace 首应用”的方案；[2026-10 重构方案](refactor-plan-2026-10.md)仅记录已完成的学习实验室建设。

## 1. 产品定位

> **构建一个 Python 自托管、单用户、可持续进化的个人 Agent：通过 CLI 接受任务，安全操作工作区，记住偏好、检索经验、沉淀 Skills，并能定时主动地完成任务。**

这是**应用优先**项目，不是面向第三方开发者的通用 Agent 框架。目标首先来自作者日常使用 OpenClaw/Hermes 的真实需求；新产品在学习与验证期间采用影子运行，不立即替换现有主力工具。

## 2. 参考对象与取舍

| 参考 | 吸收什么 | 不照搬什么 |
|---|---|---|
| [Pi](https://github.com/earendil-works/pi) | 小型 Agent 核心、工具/事件边界、原始历史与模型视图分离、可选 Durable 层 | 多包拆分、无内置权限、完整扩展生态 |
| [Hermes](https://github.com/NousResearch/hermes-agent) | 个人助手定位、记忆快照、FTS5 会话检索、Skills 学习循环、定时任务与多执行后端 | 大体量产品形态、无审查的自我修改、一次覆盖全部渠道 |
| [手写 Agent 教程](https://nano-ai.tech/agent/) | 小步垂直实现、代码级安全闸门、按需加载、有限预授权和明确局限 | 教学目录、示例级全局状态和线性功能堆叠 |

首期为单进程、单节点、单用户应用；核心不导入 CLI、调度或具体存储。工具副作用不承诺 exactly-once，会话回滚不等于外部副作用回滚。首发 CLI，聊天渠道和 JSON-RPC 后置；不做多租户、分布式队列、Graph、Agent 团队或公共框架 API。

## 3. 核心场景

| 场景 | 用户得到什么 | 验证重点 | 阶段 |
|---|---|---|---|
| **个人任务** | 在 CLI 中提交任务，获得文件/命令结果、测试证据和清晰摘要 | 循环、上下文、工作区工具、审批、沙箱、恢复 | P1/P2 |
| **学习进化** | 跨会话记住稳定偏好，找回历史细节，把有效做法复用为 Skills | 记忆快照、FTS5、压缩前记忆、技能草稿审核 | P3 |
| **例行自动化** | 定时检查 inbox/公开来源，有结果才汇报，无人值守时不越权 | 独立会话、有限预授权、心跳、成本和恢复 | P4 |
| **调研工作流** | 生成带路径/URL 引用的研究报告 | 作为一种 Skill 和只读子任务，不是独立 Research 产品 | P3 后按需 |

数据均来自 sanitized 日常任务、可重建 fixtures 或录制公开来源；运行产物写 `results/` 或 `logs/`。每个测试使用独立 workspace/state，不默认读取真实项目或凭证。

## 4. 目标架构

```text
CLI（首期） / 聊天渠道（后置）
              ↓
Personal Runtime：Conversation / Run / Approval / Scheduler
              ↓
AIAgent：循环 / 工具调用 / ContextView / 事件
              ↓
Workspace Tools / Memory / Skills / Execution Backend
              ↓
SQLite：事件、会话、任务、审批、FTS5；JSONL 仅导出
```

- **Run/Event**：每次执行可取消、恢复和审计；事件含 `event_id / parent_event_id / session_id / run_id / seq`，为以后分支保留树形关系。
- **ContextView**：模型调用前由原始事件生成；压缩只改变视图，不修改事实源。
- **学习循环**：`USER.md` 与 `MEMORY.md` 有容量上限并在会话开始时冻结快照；稳定记忆自动写入且保留审计，Skills 先草稿后审核。
- **审批与执行分离**：硬规则先于审批；工作区沙箱不可用时，写入/shell 逐条人工确认，无人值守拒绝。
- **可替换但不插件化一切**：模型、工具、执行和存储有明确接口；CLI、Memory、Skills 和 Scheduler 不进入最小 Agent 循环。

## 5. 目标目录与资产映射

```text
src/tinyagent/
├── agent/      # 循环、消息、ContextView、事件与用量
├── tools/      # 注册表、工作区工具、可选 MCP
├── policy/     # allow/ask/deny、plan/unattended
├── execution/  # local、workspace sandbox、可选 Docker
├── memory/     # USER/MEMORY、冻结快照、会话检索
├── skills/     # 按需加载、草稿审核、版本记录
├── runtime/    # Conversation、Run、Approval、Scheduler
├── channels/   # CLI；聊天渠道后置
└── cli.py      # 单用户应用入口
evals/          # personal、learning、routine 场景与 harness
tests/  examples/  docs/
```

| 现有资产 | 处置 |
|---|---|
| 循环、双 codec、MCP、Memory、Swarm | 保留可复用语义并重写；Swarm/多 Agent 后置 |
| `FileSessionStore` + `JsonlTracer` | 按 ADR-0009 演进为 SQLite + FTS5，JSONL 用于导出与迁移 |
| `TinyAgent.run` 与公共导出 | v1.0 破坏性重写，不设通用框架兼容门面 |
| Experiment Copilot 及耦合评测 | 不使用、不迁移、不作基线；P5 直接删除 |
| `learn/` 与课程资产 | 迁至 `TinyAgent-lab`；产品文档重写 |
| README、AGENTS、pyproject、架构/测试文档 | 改为个人 Agent 的使用、部署、记忆、Skills、安全和运维文档 |

## 6. 实施阶段与验收

| 阶段 | 内容 | 完成门槛 |
|---|---|---|
| **P0 已完成** | 按 [P0 执行文档](p0-execution.md) 建立 3 个任务与 fixtures、9 次 Hermes 基线、逐文件清单和回滚方案 | 任务与评分可复现；基线完整；清单无未评审项 |
| **P1 已完成** | 按 [P1 执行文档](p1-execution.md) 实现 Agent 循环、只读工作区、SQLite 事件、ContextView、CLI 审批 | 只读任务可用；原始历史不丢；配对/恢复测试通过 |
| **P2 已完成** | 按 [P2 执行文档](p2-execution.md) 实现写入/shell、沙箱与降级、Run 取消恢复、会话串行化、usage | 越界/拒绝/降级全过；补丁与测试证据可复现；无重复事件 |
| **P3 已完成** | 按 [P3 执行文档](p3-execution.md) 实现 USER/MEMORY、FTS5、压缩前记忆、Skills 草稿审核与复用 | 记忆跨会话生效；检索可追溯；未经审核技能不可执行 |
| **P4 已完成** | 按 [P4 执行文档](p4-execution.md) 实现 Scheduler、独立会话、有限预授权、心跳与本地投递 | 不错误补跑/重复执行；无人值守不越权；成本有记录 |
| **P5 已完成** | 按 [P5 执行文档](p5-execution.md) 完成三个日常任务验收、旧应用删除、学习资产外迁和文档更新 | 功能/安全/恢复 100% 通过；三门禁全绿；再决定是否替换主力工具 |

CI 至少运行 `uv run pytest`、`uv run ruff check .`、`python scripts/check_docs.py`。真实模型场景至少运行 3 轮并记录成功率、token、延迟和人工评分；质量和性能建立基线，不要求每次提升。

## 7. 已确认决策

| 编号 | 决策项 | 结论 |
|---|---|---|
| D1/D14 | 产品定位 | 应用优先的 Python 自托管个人 Agent；Hermes 产品主线 + Pi 核心边界 + 教程垂直实现 |
| D2/D19 | 学习资产 | `learn/` 与课程文档迁至独立 `TinyAgent-lab` 仓库 |
| D3 | 兼容策略 | v1.0 破坏性重写，不维护旧公共 API 兼容门面 |
| D4 | 交付形态 | 单用户应用 + 内部引擎；单发行包 + extras，不先提供通用框架 API |
| D5/D12 | 交互与接口 | 首发 CLI；聊天渠道与 JSON-RPC 后置，Runtime 首期进程内调用 |
| D6 | 持久化 | SQLite 事件/会话/任务 + FTS5；JSONL 导出；USER/MEMORY 为受限文本文件 |
| D7/D11 | 执行隔离 | 工作区沙箱优先；不可用时写/shell 逐条确认，无人值守拒绝 |
| D8 | 首期范围 | CLI + 工作区 + 学习循环 + 例行任务；无独立 Research 应用、Graph 或 Agent 团队 |
| D9/D10 | 原应用 | 不使用、不迁移 `~/projects/tsproj_ml` 相关应用与评测；直接删除 |
| D13 | 验收门槛 | 功能、安全、恢复用例 100% 通过；质量/性能以多轮基线评估 |
| D15 | 学习写入 | 稳定记忆自动写入并审计；Skills 先草稿后人工审核 |
| D16/D18 | 影子对照 | 验收前不替换现有主力；以 Hermes 为主对照，OpenClaw 仅补充 |
| D17 | P0 任务 | 定期监测与摘要、工作区任务、引用调研报告 |

## 8. 设计文档与剩余准备

- [P1 CLI 单会话与只读工作区](p1-execution.md)
- [P2 安全写入、受限 shell、沙箱与恢复](p2-execution.md)
- [P3 记忆、FTS5 检索与 Skills 学习循环](p3-execution.md)
- [P4 Scheduler、隔离会话与例行自动化](p4-execution.md)
- [P5 总验收、归档与清理](p5-execution.md)

- [P0 真实任务、基线与迁移准备](p0-execution.md)
- [ADR-0008 Personal Runtime](../10-framework/adr/0008-runtime-json-rpc.md)
- [ADR-0009 SQLite、FTS5 与记忆存储](../10-framework/adr/0009-event-store-sqlite.md)
- [ADR-0010 ContextView 与学习上下文](../10-framework/adr/0010-context-view.md)
- [ADR-0011 审批与执行安全](../10-framework/adr/0011-approval-execution.md)
- [迁移与清理清单](product-refactor-migration.md)
- [个人 Agent 场景与评测规范](../20-evals/application-scenarios.md)

P0–P5 均已完成并通过实证验收；是否替换当前 Hermes/OpenClaw 主力工具由用户另行决定。

## 相关

- [2026-10 重构方案](refactor-plan-2026-10.md) ｜ [ADR-0003](../10-framework/adr/0003-session-and-tracing.md) ｜ [ADR-0006](../10-framework/adr/0006-graph-runtime-proposal.md)
- [当前架构](../00-overview/architecture.md) ｜ [评测](../20-evals/index.md) ｜ [测试](../30-development/testing.md)
