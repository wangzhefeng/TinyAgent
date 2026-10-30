> 所属：[TinyAgent Docs](../README.md) › [概览](index.md)

# 仓库架构

## 定位

TinyAgent 是 Python 自托管、单用户、可持续进化的个人 Agent。项目采用**应用优先**结构，不以通用 Agent 框架或教学路径为目标。

## 分层

```text
CLI（当前） / 聊天渠道（后续）
              ↓
Personal Runtime：Conversation / Run / Approval / Scheduler
              ↓
AIAgent：循环 / 工具调用 / ContextView / 事件
              ↓
Workspace Tools / Memory / Skills / Execution Backend
              ↓
SQLite：事件、会话、任务、审批、FTS5；JSONL 仅导出
```

- **agent/**：Run/Event 类型与模型上下文视图。
- **runtime/**：SQLite、执行、恢复、审批、usage 与 Scheduler。
- **tools/**：工作区、学习和调度工具。
- **execution/**：本地、Seatbelt、bubblewrap 执行后端。
- **memory/**：USER/MEMORY 文件与冻结快照。
- **skills/**：正式 Skills 与待审核草稿隔离。
- **channels/**、**cli.py**：单用户 CLI。

核心不导入 CLI、调度或具体存储；工具副作用不承诺 exactly-once，会话回滚不等于外部副作用回滚。

## 当前目录

```text
src/tinyagent/
├── api.py        # v1.0 稳定公共 API
├── agent/
├── core/         # 模型、消息与工具基础协议
├── runtime/
├── tools/
├── execution/
├── memory/
├── skills/
├── channels/
├── ext/          # 可选 MCP 工具源
└── cli.py
evals/          # personal / learning / routine 场景
tests/          # 单元测试
docs/           # 唯一文档中心
```

P0–P4 已实现 CLI 单会话、只读与安全写入、沙箱、学习循环和例行自动化；P5 完成总验收与旧资产清理。实施记录见[个人 Agent 重构方案](../40-reference/refactor-plan-product.md)。

## 相关

- [repo-map](repo-map.md)
- [environment](environment.md)
- [testing](../30-development/testing.md)
