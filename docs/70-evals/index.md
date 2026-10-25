> 所属：[TinyAgent Docs](../README.md) › [评测与观测](index.md)

# L6：评测与观测

## 定位

让"哪个版本更好"变成可回答的问题：评测方法、tracing、模式间与应用版本间的量化对比。

## 规划（M5）

1. **评测集**：`evals/` 存放任务-期望对；Copilot 用 tsproj_ml 真实实验产物构造（指标提取是否正确、报告结论是否与 CSV 一致、配置生成是否通过 schema 校验）。
2. **评测 harness**：轻量 runner（框架内置 `tinyagent.evals` 或独立脚本），输出 markdown 对比表。
3. **观测**：JSONL tracer（框架自带）为基础；LangSmith 作为可选后端对照。
4. **对比实验**：三版本 Copilot（手写 / 自研框架 / LangGraph）+ 关键模式对照，同一评测集出数据、写报告。

## 现状

尚未开始；依赖 M1–M4 的产出。

## 相关

- [30-copilot](../30-copilot/index.md)：评测对象
- [50-patterns](../50-patterns/index.md)：模式对照的来源
