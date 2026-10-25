> 所属：[TinyAgent Docs](../README.md) › [LangGraph](index.md)

# L3：LangGraph 实战

## 定位

完整跟做 LangChain 官方 [agents-from-scratch](https://github.com/langchain-ai/agents-from-scratch) 课程（本仓库 `pyproject.toml` 的原始出处），以邮件助手为主线掌握：状态图与节点编排、checkpoint 持久化、interrupt 人工介入、记忆、多智能体 supervisor。

## 规划（M3）

1. `learn/level3_langgraph/` 落位课程代码（part 1 → part 3 全程完成，不留半成品）。
2. 每章一页笔记：LangGraph 的抽象与自研框架六协议的对照（checkpointer ↔ SessionStore、interrupt ↔ Guardrail/HITL）。
3. 课程完成后将 HITL 与断点能力反哺 Copilot（C2 阶段）。

## 依赖

`course` 依赖组（langgraph、langgraph-cli[inmem] 等，M0 于根 `pyproject.toml` 配置）。

## 相关

- [20-framework](../20-framework/index.md)：对照阅读的基准
- [30-copilot](../30-copilot/index.md)：C2 消费课程产出
