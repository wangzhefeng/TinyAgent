# TinyAgent 文档索引

> 本目录是 TinyAgent 的**唯一文档中心**。根 [README](../README.md) 只做项目总索引；这里按域逐步展开。
> 维护规则见 [docs-maintenance](30-development/docs-maintenance.md) 与根目录 [AGENTS.md](../AGENTS.md)。

## 按域

| 域 | 入口 | 说明 |
|---|---|---|
| 项目概览 | [00-overview/index.md](00-overview/index.md) | 定位、架构、环境与代码映射 |
| 框架与 ADR | [10-framework/index.md](10-framework/index.md) | Agent 内核、Runtime、存储、上下文与安全 |
| 评测与观测 | [20-evals/index.md](20-evals/index.md) | 个人任务、学习循环、例行自动化与 usage |
| 工程规范 | [30-development/index.md](30-development/index.md) | 编码风格、测试、文档维护与清理记录 |
| 参考资料 | [40-reference/index.md](40-reference/index.md) | 重构方案、阶段实施与迁移记录 |
| 归档 | [archive/](archive/) | 历史材料 |

## 横切主题

| 主题 | 入口 |
|---|---|
| 架构 | [00-overview/architecture.md](00-overview/architecture.md) |
| 环境搭建 | [00-overview/environment.md](00-overview/environment.md) |
| 代码 → 文档映射 | [00-overview/repo-map.md](00-overview/repo-map.md) |
| 个人 Agent 重构总纲 | [40-reference/refactor-plan-product.md](40-reference/refactor-plan-product.md) |
| 迁移与清理清单 | [40-reference/product-refactor-migration.md](40-reference/product-refactor-migration.md) |

### 实施记录

- [P0 真实任务与基线](40-reference/p0-execution.md)
- [P1 CLI 单会话](40-reference/p1-execution.md)
- [P2 安全写入与 shell](40-reference/p2-execution.md)
- [P3 记忆、检索与 Skills](40-reference/p3-execution.md)
- [P4 Scheduler 与例行自动化](40-reference/p4-execution.md)
- [P5 总验收、归档与清理](40-reference/p5-execution.md)

### 核心设计件

- [Personal Runtime](10-framework/adr/0008-runtime-json-rpc.md)
- [SQLite、FTS5 与记忆存储](10-framework/adr/0009-event-store-sqlite.md)
- [ContextView 与学习上下文](10-framework/adr/0010-context-view.md)
- [审批与执行安全](10-framework/adr/0011-approval-execution.md)
- [个人 Agent 评测规范](20-evals/application-scenarios.md)

## 渐进式披露约定

1. 每页只讲一个主题，尽量 **≤ 150 行**。
2. `index.md` 只放概览、目录和链接，不重复细节。
3. 细节页顶部放“所属”导航，底部放“相关”链接。
4. 代码目录不放长文档；新增内容统一写到本目录。
5. 功能变更必须同步更新对应文档，详见 [docs-maintenance](30-development/docs-maintenance.md)。
