> 所属：[TinyAgent Docs](../README.md) › [LangGraph](index.md)

# L3：LangGraph 实战

## 定位

完整跟做 LangChain 官方 [agents-from-scratch](https://github.com/langchain-ai/agents-from-scratch) 课程（本仓库 `pyproject.toml` 的原始出处），以邮件助手为主线掌握：状态图与节点编排、checkpoint 持久化、interrupt 人工介入、记忆、多智能体路由。

## 现状（M3 已完成，2026-10-25）

三个 part 全部实现并实跑通过（模型统一走智谱 OpenAI 兼容端点，离线 mock 邮箱，无需 Gmail OAuth）：

| 入口 | 内容 |
|---|---|
| `python -m learn.level3_langgraph.part1_from_scratch.run_part1` | **part1 从零手写**：triage 路由 + 手写 ReAct 工具循环 + 长期记忆（profile/hit_list） |
| `python -m learn.level3_langgraph.part2_langgraph.run_part2` | **part2 状态图重建**：`StateGraph` + 条件边 + 原生 function calling + `MemorySaver` 断点续跑（同 thread 追问记忆验证） |
| `python -m learn.level3_langgraph.part3_hitl.run_part3` | **part3 HITL + 多智能体**：`interrupt()` 审批 `write_email`（accept/reject）+ triage 路由到响应/运维两个智能体 |

## 课程笔记

- [LangGraph 抽象 ↔ tinyagent 六协议对照](course-notes.md)——含三 part 实测记录与教学结论

## 相关

- [20-framework](../20-framework/index.md)：对照阅读的基准（Runtime/Guardrail 扩展点即由此课程结论驱动）
- [30-copilot](../30-copilot/index.md)：C2 将把 interrupt 能力反哺 Copilot
