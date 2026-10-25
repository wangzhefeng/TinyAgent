# TinyAgent 文档索引

> 本目录是 TinyAgent 的**唯一文档中心**。根 [README](../README.md) 只做项目总索引；这里按域逐步展开。
> 维护规则见 [docs-maintenance](80-development/docs-maintenance.md) 与根目录 [AGENTS.md](../AGENTS.md)。

## 按域

| 域 | 入口 | 说明 |
|---|---|---|
| 基础与手写（L0–L1） | [10-scratch/index.md](10-scratch/index.md) | LLM API 基础、从零手写 ReAct / Plan-Execute / Reflection |
| 自研框架（L2） | [20-framework/index.md](20-framework/index.md) | tinyagent：内核、六协议、五扩展点、ADR |
| 载体应用 | [30-copilot/index.md](30-copilot/index.md) | Experiment Copilot，面向 tsproj_ml |
| LangGraph（L3） | [40-langgraph/index.md](40-langgraph/index.md) | agents-from-scratch 邮件助手课程 |
| 模式实验室（L4） | [50-patterns/index.md](50-patterns/index.md) | 路由 / 链式 / 反思 / 自纠错等架构模式 |
| 生态与协议（L5） | [60-ecosystem/index.md](60-ecosystem/index.md) | MCP、ADK、框架横评、本地部署 |
| 评测与观测（L6） | [70-evals/index.md](70-evals/index.md) | 评测方法、tracing、对比实验 |
| 工程规范 | [80-development/index.md](80-development/index.md) | 编码风格、测试、文档维护、清理记录 |
| 参考资料 | [90-reference/index.md](90-reference/index.md) | 知识笔记、学习资料、重构方案与迁移记录 |
| 归档 | [archive/](archive/) | 历史材料 |

## 横切主题

| 主题 | 入口 |
|---|---|
| 项目概览 / 架构 | [00-overview/index.md](00-overview/index.md) |
| 学习地图与里程碑 | [00-overview/learning-path.md](00-overview/learning-path.md) |
| 术语约定 | [00-overview/terminology.md](00-overview/terminology.md) |
| 环境搭建 | [00-overview/environment.md](00-overview/environment.md) |
| 代码 → 文档映射 | [00-overview/repo-map.md](00-overview/repo-map.md) |
| 重构方案（评审稿） | [90-reference/refactor-plan-2026-10.md](90-reference/refactor-plan-2026-10.md) |

## 渐进式披露约定

1. 每页只讲一个主题，尽量 **≤ 150 行**。
2. `index.md` 只放概览、目录和链接，不重复细节。
3. 细节页顶部放"所属"导航，底部放"相关"链接。
4. 代码目录不放长文档；新增内容统一写到本目录。
5. 功能变更必须同步更新对应文档，详见 [docs-maintenance](80-development/docs-maintenance.md)。
