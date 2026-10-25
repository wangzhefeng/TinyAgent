# ADR-0001：内核 agent_loop 与六协议

> 所属：[TinyAgent Docs](../../README.md) › [自研框架](../index.md) › ADR

日期：2026-10-25 ｜ 状态：v0.1 已实现

## 背景

L1 手写三范式（M1 完成）验证了 Agent 的最小内核：生成 → 解析工具调用 → 执行 → 回填 → 终止。
手写版同时暴露了四类问题（Action 解析切片 bug、固定两次调用截断循环、模型自编 Observation、
超时/拥堵无退避），这些直接构成框架内核的设计输入。对标：smolagents 的极简 loop、
OpenAI Agents SDK 的 `agent.run` 循环。

## 决策

1. **内核只有一个函数** `agent_loop(model, codec, registry, question, ...)`，约 30 行，
   不依赖任何具体模型/工具/存储实现。
2. **六协议**（`typing.Protocol`，全部可替换）：
   - `ChatModel.chat(messages, tools) -> ModelReply`：唯一模型抽象；
   - `Tool`（`spec` + `call`）：工具统一为数据描述 + 可调用；
   - `SessionStore`：消息与状态的持久化（对齐 LangGraph checkpointer 语义的子集）；
   - `Tracer.emit(event)`：事件流（默认 JSONL，可换 LangSmith）；
   - `Guardrail`：on_input / on_action / on_output 三钩子；
   - `Memory`：短期对话缓冲（长期记忆 v0.2+）。
3. **终止条件**：codec 判定无工具调用（Final）或达到 `max_steps`（防失控，默认 6）。
4. **依赖注入而非继承**：`TinyAgent` 门面只是组装器，任何组件都可换。

## 后果

- 优点：每行内核可讲清（教学目标）；M1 的四个教训都有落点（解析修复在 codec、
  循环有界、幻觉约束在 prompt 模板、重试在 ChatModel）。
- 代价：v0.1 无流式、无并行工具调用（记入 v0.2+ 演进）。

## 相关

- [ADR-0002 双 codec](0002-call-codec.md) ｜ [ADR-0003 session 与 tracing](0003-session-and-tracing.md)
