> 所属：[TinyAgent Docs](../README.md) › [自研框架](index.md)

# L2：自研框架 tinyagent

## 定位

教学级、可扩展的 Agent 框架：把 L1 手写内核沉淀为库，逐级对标成熟框架补齐抽象。**教学级**指内核足够小、每行可讲清；**可扩展**指一切会长大的部分都隔离在协议接口之后。

## 设计要点

- **六协议**：`ChatModel`（仅依赖 OpenAI 兼容协议）/ `Tool` / `SessionStore` / `Tracer` / `Guardrail` / `Memory`；核心是约 30 行的 `agent_loop`。
- **五扩展点**：`CallCodec`（ReAct 文本 ↔ 原生工具调用编解码）、钩子中间件、`Runtime`（loop → 预留 graph）、注册表 + `ext/` 命名空间、版本化公共 API `tinyagent.api`。
- **版本演进**：v0.1 loop + 双 codec + 文件 session + JSONL tracer → v0.2 guardrail + memory + API 冻结 → v0.3 handoff + MCP 工具源 + 多智能体 → v0.4 graph runtime 预研 + LangChain 适配器。
- 每个抽象配一篇 ADR（本目录 `adr/`，M2 建立），说明对标框架与简化理由。

## 现状（v0.1 已实现，2026-10-25）

`packages/tinyagent-core/src/tinyagent/`（发行名 `tinyagent-core`，导入名 `tinyagent`）：

| 模块 | 职责 |
|---|---|
| `core/protocols.py` | **六协议**定义（ChatModel / Tool / SessionStore / Tracer / Guardrail / Memory） |
| `core/loop.py` | `agent_loop` 内核（ADR-0001） |
| `core/llm.py` | `OpenAIChatModel`：provider 预设（智谱/DeepSeek/OpenAI）+ 重试阶梯 |
| `core/tools.py` | `@tool` 装饰器（类型注解→JSON Schema）+ `ToolRegistry`（参数校验/未知参数回填） |
| `core/session.py` / `tracer.py` | `FileSessionStore` / `JsonlTracer`（ADR-0003） |
| `core/guardrails.py` | `CompositeGuardrail` + `AllowlistGuardrail`（Copilot 安全边界雏形） |
| `codecs/` | `ReactTextCodec`（含 M1 冒号 bug 回归）与 `NativeCodec` 双编解码（ADR-0002） |
| `agents/react_agent.py` | `TinyAgent` 门面：声明式组装六协议 |
| `api.py` | 版本化公共 API（唯一稳定导入面） |

验证：单测 20/20（mock 无 key，含 M1 教训回归）+ 真实 API 全链路（L2 demo：事件流 / 会话持久化 / 工具往返）。

## ADR

- [ADR-0001 内核与六协议](adr/0001-agent-loop-and-protocols.md)
- [ADR-0002 双 codec](adr/0002-call-codec.md)
- [ADR-0003 session 与 tracing](adr/0003-session-and-tracing.md)
- [ADR-0004 handoff 与 Swarm](adr/0004-handoff-and-swarm.md)（v0.3 已实现）
- [ADR-0005 MCP 工具源](adr/0005-mcp-tool-source.md)（v0.3 已实现，extras `mcp`）

## 演进

v0.1（M2）loop + 双 codec + 文件 session + JSONL tracer + 单测 → v0.2（M2 期间随 C1 落地 guardrail 应用 + memory 语义）→ **v0.3（M4，已实现）handoff/Swarm + MCP 工具源（`tinyagent.ext.mcp`）** → v0.4（M5+）graph runtime 预研 + LangChain 适配器。`hello_agents/src/`（复刻版）作为对照保留，其能力按版本渐进并入后移除。

## 相关

- [10-scratch](../10-scratch/index.md)：手写内核是框架的前身
- [重构方案 §4](../90-reference/refactor-plan-2026-10.md)：框架设计全文
