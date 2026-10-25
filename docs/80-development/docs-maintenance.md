> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 文档维护规范

## 1. 基本原则

1. **唯一文档中心**：项目级文档全部放 `docs/`；代码目录只放代码。
2. **渐进式披露**：入口页只给概要和目录，细节拆到子页面。
3. **单页单主题**：每页尽量 ≤ 150 行；超过就拆页。
4. **链接优先**：不复制内容，用相对链接指向唯一来源。
5. **根 README 是总索引**：只放项目定位、快速索引、快速开始、目录概览和文档入口。
6. **术语统一**：见[术语约定](../00-overview/terminology.md)。

## 2. 目录约定

```text
docs/
├── README.md           # 文档总索引
├── 00-overview/        # 概览、架构、学习地图、术语、环境、代码→文档映射
├── 10-scratch/         # L0–L1 基础与手写
├── 20-framework/       # L2 自研框架（含 adr/）
├── 30-copilot/         # 载体应用
├── 40-langgraph/       # L3 LangGraph
├── 50-patterns/        # L4 模式实验室
├── 60-ecosystem/       # L5 生态与协议
├── 70-evals/           # L6 评测与观测
├── 80-development/     # 工程规范
├── 90-reference/       # 参考资料、知识笔记、重构方案与迁移记录
├── images/             # 图片
└── archive/            # 历史材料（非正文）
```

## 3. 页面结构

- 正文页顶部导航：`> 所属：[TinyAgent Docs](../README.md) › [域](index.md)`。
- 正文单一主题；底部可加"相关"链接。
- 命名：小写短横线；入口统一 `index.md`。

## 4. 检查

```bash
python scripts/check_docs.py
```

报告超过 150 行的文档、失效相对链接、`docs/` 外的 markdown（根 README / AGENTS 除外；`database/` 语料属数据，豁免）。

## 5. 变更联动

代码变更必须按下表联动文档，完整映射见 [repo-map](../00-overview/repo-map.md) 与 [AGENTS.md](../../AGENTS.md) 第 3 节。
