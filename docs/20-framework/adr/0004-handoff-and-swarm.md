# ADR-0004：Handoff 与多智能体（Swarm）

> 所属：[TinyAgent Docs](../../README.md) › [自研框架](../index.md) › ADR

日期：2026-10-25 ｜ 状态：v0.3 已实现

## 背景

对标 OpenAI Agents SDK 的 handoffs 与 LangGraph 的多 agent 图路由（L3 课程 part3 已验证
triage → 响应/运维双智能体模式）。v0.1 的单 `TinyAgent` 无法表达控制权转移。

## 决策

1. **handoff 实现为普通工具**：`Swarm` 给每个成员注入 `transfer_to_<name>(reason)`
   工具；工具结果带 `HANDOFF_TO:<name>` 标记。
2. **`Swarm` 运行器**：持有 `agents: dict[str, TinyAgent]` 与入口名；运行当前 agent，
   扫描其消息中的 handoff 标记——命中则切换 agent 继续同一问题（携带历史），未命中则返回。
3. `max_handoffs`（默认 3）防乒乓死循环。
4. 顺序式多智能体（planner→executor→…）不进内核：那是应用层编排（Copilot C3 直接
   组装多个 `TinyAgent`），框架只抽象"对等转移"这一最小语义。

## 后果

- 与 codec/loop 完全正交，不改内核一行；
- supervisor 模式作为应用编排示例放 `learn/level4_patterns/supervisor.py`。

## 相关

- [ADR-0001 内核与六协议](0001-agent-loop-and-protocols.md)
