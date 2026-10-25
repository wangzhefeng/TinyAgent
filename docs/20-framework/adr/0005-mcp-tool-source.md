# ADR-0005：MCP 工具源

> 所属：[TinyAgent Docs](../../README.md) › [自研框架](../index.md) › ADR

日期：2026-10-25 ｜ 状态：v0.3 已实现

## 背景

工具的另一个来源：MCP server（L5 生态）。目标是一个 MCP server 的工具能被
tinyagent 直接挂载（方案 M4 验收项），同时本仓库的 Copilot 工具能以 MCP server
形态供任意客户端使用（双向）。

## 决策

1. `tinyagent.ext.mcp.MCPToolSource`：以 stdio 方式拉起/连接 MCP server，
   `list_tools` 的 schema 直接映射为 `ToolSpec`；`call_tool` 结果取首个 text content。
2. 上下文管理器形态：`with MCPToolSource(command).tools() as tools:`——连接生命周期
   显式、退出即关；工具调用转发到 server 进程执行（本仓库只读 server，安全边界在
   server 侧实现）。
3. MCP 依赖放 extras：`pip install tinyagent-core[mcp]`，不进核心依赖。

## 后果

- `ToolRegistry` 无需感知来源：MCP 工具与 `@tool` 函数混用；
- stdio 之外（SSE/streamable HTTP）留待后续，接口已按"command"抽象隔离。

## 相关

- [ADR-0002 双 codec](0002-call-codec.md) ｜ [60-ecosystem MCP 笔记](../../60-ecosystem/index.md)
