# ADR-0007：长期记忆（兑现 hello_agents 的空壳设计）

> 所属：[TinyAgent Docs](../../README.md) › [自研框架](../index.md) › ADR

日期：2026-10-25 ｜ 状态：v0.3.1 已实现

## 背景

`hello_agents/src/memory/` 在 README 中承诺 embedding 检索 + qdrant/neo4j 存储，
但源码为 8 行空壳。删除 hello_agents 前，其设计意图需要以真实现兑现（能力并入）。

## 决策

1. **两级记忆**：`ListMemory`（短期，内存消息缓冲，实现 Memory 协议）+
   `FileLongTermMemory`（长期，JSONL 存储）。
2. **检索策略自适应**：有 API key 时用 OpenAI 兼容 embedding（默认智谱
   `embedding-3`）做余弦相似度检索；不可用时自动退化为字符 bigram 重叠打分——
   无重依赖、离线可用，且接口不变。
3. **拒绝假实现**：qdrant/neo4j 后端不并入（无法在无服务环境下验证），
   留待真实需求出现时以 `tinyagent[vector]` extras 承接。
4. 存储路径遵循 outputs 约定：默认 `logs/tinyagent/memory.jsonl`，不入库。

## 后果

- 六协议中的 `Memory` 有了完整落地；ReflectionAgent/PlanAndSolveAgent 同批并入
  （`hello_agents/src/agents` 中 tinyagent 参数化门面未覆盖的两种编排型 agent）。
- 其余 hello_agents 能力确认已被覆盖：多 provider LLM → `OpenAIChatModel` 预设；
  simple/react/tool_aware/function_call 四种 agent → `TinyAgent` 参数化；
  工具注册/链 → `ToolRegistry` 与 patterns 实验室。`async_executor` 不并入
  （无异步需求，留待 v0.4+）。

## 相关

- [ADR-0001 内核与六协议](0001-agent-loop-and-protocols.md)
