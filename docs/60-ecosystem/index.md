> 所属：[TinyAgent Docs](../README.md) › [生态与协议](index.md)

# L5：生态与协议

## 定位

Agent 之外的生态位：工具协议（MCP）、其他开发框架（横评）、本地部署、以及被移出主线的平台类工具。

## 现状（迁移期）

| 现有代码 | 说明 | 去向 |
|---|---|---|
| `src/mcp_dev/` | FastMCP server（weather：tool/resource/prompt）+ 三种 client | `learn/level5_ecosystem/mcp/`，升级为真实工具 server |
| `src/adk_dev/` | Google ADK 单/多智能体示例 | `learn/level5_ecosystem/adk/`，补运行说明 |
| `hello_agents/test/framework/` | langgraph / agentscope / autogen / camel 练习 | `learn/level5_ecosystem/frameworks/`，整理为横评 + 对比笔记 |
| `hello_agents/test/local_server/` | ollama / vllm 客户端 | `learn/level5_ecosystem/deployment/` |
| `src/TinyAgent/down_model.py` | 本地模型下载 | `learn/level5_ecosystem/deployment/` |
| `src/dify_dev/` | 空壳 TODO | 删除（已决策） |

## 规划（M4/M5）

1. **MCP 双向**：写一个面向 tsproj_ml 的真实工具 server；自研框架作为 MCP client 挂载（框架 v0.3 工具源）。
2. **框架横评**：LangGraph / AgentScope / AutoGen / CAMEL 各保留"读设计 + 笔记 + 官方 quickstart"，深入开发只留 LangGraph 与 ADK。
3. **A2A**：协议调研笔记 + 最小 demo（低优先级）。
4. **部署**：Ollama / vLLM 以 OpenAI 兼容协议接入自研框架。

## 相关

- [20-framework](../20-framework/index.md)：MCP client 是框架 v0.3 扩展点
- [30-copilot](../30-copilot/index.md)：C3 工具 server 化
