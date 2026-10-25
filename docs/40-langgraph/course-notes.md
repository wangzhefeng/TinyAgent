> 所属：[TinyAgent Docs](../README.md) › [LangGraph](index.md)

# 课程笔记：LangGraph 抽象 ↔ tinyagent 六协议对照

> 依据 [agents-from-scratch](https://github.com/langchain-ai/agents-from-scratch) 课程（邮件助手主线），实现在 `learn/level3_langgraph/`，模型统一走智谱 OpenAI 兼容端点。

## 三个 part 的实现结构

| Part | 主题 | 代码 | 关键点 |
|---|---|---|---|
| 1 | 从零手写 | `part1_from_scratch/` | triage 路由 + 手写 ReAct 工具循环 + 长期记忆（profile/hit_list）；不依赖任何框架 |
| 2 | LangGraph 重建 | `part2_langgraph/` | `StateGraph`（triage 节点 + 响应智能体节点 + 条件边）、`add_messages`/reducer 状态、原生 function calling、`MemorySaver` checkpointer 断点续跑 |
| 3 | HITL + 多智能体 | `part3_hitl/` | `interrupt()` 人工审批 write_email（accept/reject/edit 三态）、triage 路由到响应/运维两个智能体 |

## 抽象对照表

| LangGraph 概念 | 本仓库对应 | 说明 |
|---|---|---|
| `StateGraph` / 节点 / 条件边 | `Runtime` 扩展点（v0.4 规划） | tinyagent v0.1 是循环内核；图编排是预留的运行时演进方向 |
| `add_messages` reducer | `agent_loop` 的 messages 累积 + `Memory` 协议 | 状态合并语义相同：追加而非覆盖 |
| `MemorySaver` / checkpointer | `FileSessionStore` | 语义子集对齐（ADR-0003）：每步持久化、按 thread/session 恢复 |
| `interrupt()` / `Command(resume=...)` | `Guardrail.on_action` + HITL 钩子（v0.2 规划） | LangGraph 用暂停图实现审批；tinyagent 以护栏拦截实现，语义等价 |
| `bind_tools` 原生工具 | `NativeCodec` | 同为 OpenAI function calling 形态 |
| ToolNode / 工具循环 | `agent_loop` + `ToolRegistry` | 差异：LangGraph 把工具做成图节点；tinyagent 在循环内联执行 |
| 多智能体（路由到子 agent） | handoff（v0.3 规划） | LangGraph 条件边天然支持；tinyagent 以 handoff 扩展点承接 |

## 实测记录（2026-10-25，glm-5.3-flash）

- **part1**：triage 三分类正确（respond/ignore/notify）；手写文本协议下模型倾向直接输出 Final Draft 而不调用 `write_email`——需提示词强制 + 框架兜底（从 Final Draft 落草稿）。
- **part2**：原生 function calling 下工具调用可靠；checkpointer 在同一 thread 的第二轮正确记住了第一轮邮件内容。
- **part3**：`interrupt` 在 `write_email` 处暂停图，`Command(resume={"type": ...})` 恢复；运维邮件被路由到第二个智能体（不回信、登记提醒）。

## 教学结论

1. 文本协议（ReAct prompt）对模型的服从性要求高，生产形态应默认原生 function calling——印证了 tinyagent 双 codec 设计：文本 codec 保留教学价值，native codec 承载可靠性。
2. LangGraph 的核心贡献是**把控制流变成显式图 + 可持久化状态**；tinyagent 的 SessionStore/Tracer/Guardrail 覆盖其中最有教学价值的子集，图编排留给 Runtime 扩展点。
3. `interrupt` 的实现本质 = checkpointer + 暂停语义，而非新原语——先有持久化，才有人机协同。
