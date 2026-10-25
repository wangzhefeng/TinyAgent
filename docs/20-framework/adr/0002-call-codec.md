# ADR-0002：工具调用编解码器（CallCodec）

> 所属：[TinyAgent Docs](../../README.md) › [自研框架](../index.md) › ADR

日期：2026-10-25 ｜ 状态：v0.1 已实现

## 背景

同一套 agent_loop 需要同时支持两种工具调用形态：

- **ReAct 文本协议**：工具写入 system prompt，模型输出 `Action/Action Input`，
  框架解析文本——教学价值高（L1 手写版即此），但解析脆弱（M1 修过冒号切片 bug、
  幻觉 Observation）。
- **原生 function calling**：工具以 JSON Schema 传给 API，模型返回结构化
  `tool_calls`——稳健，是生产形态。

## 决策

1. 编解码抽象为 `CallCodec` 协议，两个方法：
   - `render_tools(specs) -> RenderedTools`：文本片段（进 system）或原生 specs（进请求）；
   - `parse(reply) -> ToolAction | FinalAnswer`：统一解码为「一次工具调用」或「最终答案」。
2. **ReActTextCodec** 移植 L1 实现并固化修复：冒号切片、缺失 Observation 补全、
   system prompt 内置四条反幻觉规则。
3. **NativeCodec** 将 `ToolSpec` 转为 OpenAI tools 参数，解码 `tool_calls`。
4. codec 对 Observation 回填也负责（react 用 user 消息包裹，native 用 tool 角色）。

## 后果

- 内核对协议形态零感知；新增协议（如受限 JSON）只需新 codec，不动内核——这是
  框架五个扩展点中的第一个落地。
- ReAct 文本协议保留在教学示例与单测回归中（含冒号 bug 的回归用例）。

## 相关

- [ADR-0001 内核与六协议](0001-agent-loop-and-protocols.md)
