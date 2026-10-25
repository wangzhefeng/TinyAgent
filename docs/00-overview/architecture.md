> 所属：[TinyAgent Docs](../README.md) › [概览](index.md)

# 仓库架构

## 双主线 + 载体应用

```text
学习路径 learn/（L0–L6，横向递进）──每升一级──▶ 自研框架 packages/tinyagent（纵向进化）
                     │
                     └──每级用新能力增强同一应用──▶ apps/experiment_copilot
```

- **学习路径**：每级一组可运行代码 + README（目标 / 运行方式 / 进度）。
- **自研框架**：从 L1 的最小内核逐级进化到具备 memory / session / tracing / handoff 的完整框架，每一级对标一个成熟框架源码。
- **载体应用**：面向时序预测实验仓库的实验副驾驶，默认操作 `~/projects/tsproj_ml`。

## 当前结构（M0 迁移已完成）

2026-10-25 M0 完成：学习代码迁入 `learn/`，RAG 应用迁入 `apps/experiment_copilot/doc_qa/`，框架示例位建于 `packages/tinyagent-core/examples/`。残留 `hello_agents/`（`src/` 与 `version.py`）为 M2 重构迁入前的过渡。映射明细见[重构方案](../90-reference/refactor-plan-2026-10.md)与[repo-map](repo-map.md)。

## 目标结构

目标目录树、迁移映射与实施阶段统一维护在[重构方案（评审稿）](../90-reference/refactor-plan-2026-10.md)，本页不重复。方案要点：

```text
learn/                  # L0–L6 学习路径
packages/tinyagent-core/# 自研框架（uv workspace 成员，导入名 tinyagent）
apps/experiment_copilot/# 载体应用
evals/  tests/          # 评测与测试
docs/                   # 唯一文档中心（本目录）
```

## 相关

- [learning-path](learning-path.md)：各级学什么、产出什么
- [repo-map](repo-map.md)：改代码时该更新哪篇文档
