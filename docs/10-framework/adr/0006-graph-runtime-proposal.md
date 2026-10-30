# ADR-0006：Graph Runtime 预研（v0.4 提案）

> 所属：[TinyAgent Docs](../../README.md) › [自研框架](../index.md) › ADR

日期：2026-10-25 ｜ 状态：**预研提案（未实现）**

## 背景

L3 课程与 M4 多智能体实践揭示了循环内核的边界：当控制流需要**条件分支、并行
节点、跨会话恢复的显式编排**时，agent_loop 的线性迭代表达力不足。LangGraph 的
解法是显式状态图 + checkpointer（当前 Runtime 设计见 [ADR-0008](0008-runtime-json-rpc.md)）。

## 提案（v0.4 若实现）

1. **不改公共 API**：`Runtime` 协议内化为编排策略——`LoopRuntime`（现状）与
   `GraphRuntime`（新）对 `TinyAgent.run` 透明。
2. **GraphRuntime 最小集**：节点 = 可调用（含 agent/工具/路由函数）；边 = 静态或
   条件函数；状态 = 可 JSON 化 dict（复用 `FileSessionStore` 持久化，每节点后落盘，
   对齐 LangGraph checkpointer 语义）。
3. **interrupt 复用会话语义**：图执行前持久化 → 暂停即返回 pending 状态 →
   `run(resume=...)` 从检查点继续（与 ADR-0003 的 SessionStore 天然衔接）。
4. **优先组合而非替代**：Swarm/Supervisor 保持现有实现；GraphRuntime 只服务
   确实需要图的场景（并行工具、复杂审批流）。

## 为何暂缓

M0–M5 的全部验收场景（工具循环、多智能体、MCP、评测）均已被循环内核 + 应用层
编排覆盖；引入图运行时的复杂度收益比当前不成立。留待出现真实图需求（如并行
工具调用、复杂 HITL 流）再实现——本 ADR 即那时的设计底稿。

## 相关

- [ADR-0001 内核与六协议](0001-agent-loop-and-protocols.md)
- [ADR-0003 session 与 tracing](0003-session-and-tracing.md)
