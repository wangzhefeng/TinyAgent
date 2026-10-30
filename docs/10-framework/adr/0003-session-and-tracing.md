# ADR-0003：会话持久化与事件追踪

> 所属：[TinyAgent Docs](../../README.md) › [自研框架](../index.md) › ADR

日期：2026-10-25 ｜ 状态：v0.1 已实现

## 背景

对照 LangGraph（checkpointer/interrupt）与 OpenAI SDK（sessions/tracing），
会话可恢复与运行可观测是成熟框架的标配。教学级 v0.1 需要零依赖、可讲清的实现。

## 决策

1. **FileSessionStore**：每个会话一个 JSONL 文件（`sessions/<id>/messages.jsonl`），
   `append_message / load_messages / save_state / load_state`；状态为可 JSON 化 dict。
   接口语义对齐 LangGraph checkpointer 的子集（写入时机：每步之后），
   未来可平滑替换实现。
2. **JsonlTracer**：`traces/<run_id>.jsonl` 事件流，事件含 `ts / event / data`；
   标准事件：`run_start / llm_call / llm_reply / tool_call / tool_result / run_end`。
   追踪器为可选注入（None 即不落盘），不侵入内核。
3. 路径约定：默认仓库根 `logs/tinyagent/`（受 `.gitignore` 的 `logs/` 覆盖，不入库）。

## 后果

- 单测用 `tmp_path` 验证往返；JSONL 可被后续 UI 回放工具直接消费（事件溯源）。
- v0.1 无压缩与轮转（长会话文件增长可接受，教学规模）。

## 相关

- [ADR-0001 内核与六协议](0001-agent-loop-and-protocols.md)
