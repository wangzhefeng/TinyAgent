# TinyAgent 文档

本文档中心只描述**当前产品的使用、设计、验证和开发方式**。根 [README](../README.md) 提供项目入口与快速开始。

## 目录职责

| 目录 | 只放什么内容 | 入口 |
|---|---|---|
| `usage/` | 安装、模型配置、CLI、工作区、状态与运行产物 | [使用指南](usage/guide.md) |
| `architecture/` | 当前模块、公共 API、能力边界与架构决策 | [架构概览](architecture/overview.md) |
| `evaluation/` | 当前 fixtures、任务契约、评分规则与验证基线 | [评测规范](evaluation/scenarios.md) |
| `development/` | 编码、测试、文档维护、开发学习教程、提交规则与下一阶段 | [开发指南](development/contributing.md) |

## 常用入口

- 第一次使用：[使用指南](usage/guide.md)
- 查看当前设计：[架构概览](architecture/overview.md)
- 修改代码前：[开发指南](development/contributing.md)
- 学习 Agent 开发：[开发学习教程](development/tutorials/README.md)
- 规划后续工作：[下一阶段方向评审](development/next-phase.md)

## 架构决策

[设计决策](architecture/decisions.md)统一记录 Personal Runtime、SQLite 与记忆存储、ContextView、执行安全和 MCP 工具源的选择原因与当前边界。

## 页面规则

- 一个页面只解决一个主题，尽量不超过 150 行。
- 页面顶部提供返回本索引的导航，细节通过相对链接连接。
- 代码目录不放项目长文档；新增文档归入上述四个目录之一。
- 修改代码时同步对应现行文档，并运行 `uv run python scripts/check_docs.py`。
