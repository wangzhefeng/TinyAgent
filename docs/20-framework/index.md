> 所属：[TinyAgent Docs](../README.md) › [自研框架](index.md)

# L2：自研框架 tinyagent

## 定位

教学级、可扩展的 Agent 框架：把 L1 手写内核沉淀为库，逐级对标成熟框架补齐抽象。**教学级**指内核足够小、每行可讲清；**可扩展**指一切会长大的部分都隔离在协议接口之后。

## 设计要点

- **六协议**：`ChatModel`（仅依赖 OpenAI 兼容协议）/ `Tool` / `SessionStore` / `Tracer` / `Guardrail` / `Memory`；核心是约 30 行的 `agent_loop`。
- **五扩展点**：`CallCodec`（ReAct 文本 ↔ 原生工具调用编解码）、钩子中间件、`Runtime`（loop → 预留 graph）、注册表 + `ext/` 命名空间、版本化公共 API `tinyagent.api`。
- **版本演进**：v0.1 loop + 双 codec + 文件 session + JSONL tracer → v0.2 guardrail + memory + API 冻结 → v0.3 handoff + MCP 工具源 + 多智能体 → v0.4 graph runtime 预研 + LangChain 适配器。
- 每个抽象配一篇 ADR（本目录 `adr/`，M2 建立），说明对标框架与简化理由。

## 现状（迁移期）

现有 `hello_agents/src/` 是对 Datawhale Hello Agents 的复刻，约 3800 行，已具备：

```text
core/      Agent 基类、HelloAgentsLLM（多 provider）、消息、配置、异常
agents/    Simple / ReAct / Reflection / PlanAndSolve / FunctionCall / ToolAware
tools/     注册机制、工具链、异步执行器、内置 calculator 与 search
memory/    embedding、qdrant / neo4j 存储、manager
```

M2 将其**重构迁入** `packages/tinyagent-core/src/tinyagent/`（发行名 `tinyagent-core`、导入名保持 `tinyagent`；非照搬）：六协议化接口、`@tool` 装饰器 + 类型注解生成 JSON Schema、补齐 session / tracing / guardrail、建立单测。`agent_usage/hello_world.py` 随新 API 改写为 `examples/`。

## 相关

- [重构方案 §3](../90-reference/refactor-plan-2026-10.md)：框架设计全文
- [10-scratch](../10-scratch/index.md)：手写内核是框架的前身
