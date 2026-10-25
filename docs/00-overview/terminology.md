> 所属：[TinyAgent Docs](../README.md) › [概览](index.md)

# 术语约定

中文正文 + 英文代码标识符；翻译不统一的术语按下表执行。

| 术语 | 约定 | 说明 |
|---|---|---|
| Agent | 智能体（保留英文亦可） | 用 LLM 决定控制流的系统 |
| tool calling / function calling | 工具调用 | function calling 为历史同义术语，首次出现时注明 |
| ReAct | 不译 | Reasoning + Acting 思考框架 |
| Plan-and-Execute | 规划-执行 | |
| Reflection | 反思 | |
| MCP | MCP（Model Context Protocol，模型上下文协议） | 首次出现标全称 |
| A2A | A2A（Agent2Agent 协议） | |
| HITL | 人工介入（human-in-the-loop） | |
| checkpoint | 检查点 | 会话/状态持久化 |
| guardrail | 护栏 | 输入/输出/动作校验 |
| handoff | 移交 | Agent 间控制权转移 |
| eval | 评测 | |
| memory | 记忆 | 短期（消息历史）/ 长期（外部存储） |
| session | 会话 | |
| tracing | 追踪 | 运行事件记录 |
| RAG | RAG（检索增强生成） | |
| multi-agent | 多智能体 | |
| inference / reasoning | 推断 / 推理 | 沿用 TinyLLM 术语约定；`inference-time scaling` 写"推断时扩展" |

新增术语时：先查本表；未收录且易歧义的，先补表再使用。
