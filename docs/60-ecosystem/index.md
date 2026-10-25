> 所属：[TinyAgent Docs](../README.md) › [生态与协议](index.md)

# L5：生态与协议

## 定位

Agent 之外的生态位：工具协议（MCP）、其他开发框架（横评）、本地部署。

## 内容导航

| 页面 | 内容 |
|---|---|
| [MCP 笔记（一）：架构与通信协议](mcp-protocol.md) | JSON-RPC、stdio/SSE 传输、交互生命周期 |
| [MCP 笔记（二）：功能](mcp-features.md) | Tools / Resources / Prompt / Sampling 与发现机制 |
| [MCP 笔记（三）：SDK 与客户端](mcp-clients.md) | FastMCP、mcp.json 配置、smolagents 代码客户端 |

## 现状（M0 已迁入）

| 代码 | 说明 | 来源 |
|---|---|---|
| `learn/level5_ecosystem/mcp/` | FastMCP server（weather 三要素示例）+ stdio/remote/packages 三种 client | `src/mcp_dev/` |
| `learn/level5_ecosystem/adk/` | Google ADK 单/多智能体示例 | `src/adk_dev/` |
| `learn/level5_ecosystem/frameworks/langgraph/` | workflow + 三步 QA 助手两个练习 | `hello_agents/test/framework/framework_langgraph/` |
| `learn/level5_ecosystem/frameworks/agentscope/` | 角色扮演、结构化输出等练习 | 同上 |
| `learn/level5_ecosystem/frameworks/autogen/` | 团队聊天练习 | 同上 |
| `learn/level5_ecosystem/deployment/` | ollama / vllm 客户端与服务脚本、模型下载 | `hello_agents/test/local_server/`、`src/TinyAgent/down_model.py` |

框架要点笔记（迁入吸收）：

* **LangGraph** = 状态机 + 有向图；基本要素：全局状态（State）、节点（Nodes）、边（Edges）。
* **CAMEL** 角色扮演：AI 用户（AI User）与 AI 助理（AI Assistant）双角色对话；
  引导性提示（Inception Prompting）四要素：明确自身角色、告知协作者角色、定义共同目标、设定行为约束和沟通协议。
* **本地部署**：[vLLM](https://docs.vllm.ai/en/latest/getting_started/installation/)、[Ollama](https://ollama.com/)，
  均以 OpenAI 兼容协议接入。

## 规划（M4/M5）

1. **MCP 双向**：写一个面向 tsproj_ml 的真实工具 server；自研框架作为 MCP client 挂载（框架 v0.3 工具源）。
2. **框架横评**：LangGraph / AgentScope / AutoGen 各保留"读设计 + 笔记 + 官方 quickstart"，深入开发只留 LangGraph 与 ADK。
3. **A2A**：协议调研笔记 + 最小 demo（低优先级）。
4. **部署**：Ollama / vLLM 以 OpenAI 兼容协议接入自研框架。

## 相关

- [20-framework](../20-framework/index.md)：MCP client 是框架 v0.3 扩展点
- [30-copilot](../30-copilot/index.md)：C3 工具 server 化
