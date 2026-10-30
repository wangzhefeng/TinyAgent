> 所属：[TinyAgent Docs](../README.md) › [生态与协议](index.md)

# MCP 笔记（三）：SDK 与客户端

> 迁入自 `src/mcp_dev/README.md`（2026-10 拆分为三页）。

## SDK 概览

官方 SDK（JavaScript / Python 等）处理协议级通信、能力注册与发现、消息序列化、连接管理和错误处理，
让开发者专注应用功能。

* [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
* [MCP 官网](https://modelcontextprotocol.io/introduction)

最小 server 示例见 `learn/level5_ecosystem/mcp/server.py`（FastMCP 的 `@mcp.tool()` /
`@mcp.resource()` / `@mcp.prompt()` 三要素齐全），本地调试：`mcp dev server.py`。

## 用户界面客户端

* **聊天界面**：Claude 桌面版——最突出的 MCP 客户端，集成各种 MCP 服务器。
* **交互式开发**：Cursor（编辑器内集成、实时工具调用）、Continue.dev（VS Code 连接 MCP 服务器）。

## 配置：mcp.json

宿主用配置文件管理服务器连接，主流宿主间保持一致：

```json
{
  "servers": [
    {
      "name": "File Explorer",
      "transport": {
        "type": "stdio",
        "command": "python",
        "args": ["/path/to/file_explorer_server.py"],
        "env": {"GITHUB_TOKEN": "your_github_token"}
      }
    }
  ]
}
```

* `stdio`（本地）：`command` + `args` 启动服务器子进程；`env` 字段传环境变量（服务器内用
  `os.environ.get("GITHUB_TOKEN")` 读取，缺失时直接 raise）。
* `sse`（远程）：`transport` 换为 `{"type": "sse", "url": "https://example.com/mcp-server"}`。

> MCP 规范仍在演进，配置方法处于变化中，以当前官方最佳实践为准。

## 代码客户端

在代码中把 MCP 服务器的工具接入 LLM。以 `smolagents` 为例：

```python
from smolagents import ToolCollection, CodeAgent
from mcp import StdioServerParameters

server_parameters = StdioServerParameters(command="uv", args=["run", "server.py"])

with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
    agent = CodeAgent(tools=[*tool_collection.tools], model=model)
    agent.run("What's the weather in Tokyo?")
```

* 远程服务器：传 `SSEServerParameters` / `{"url": ...}`；
* 连接 MCP 包（如 `pubmedmcp`）：`StdioServerParameters(command="uv", args=["--quiet", "pubmedmcp@0.1.3"], env={...})`；
* 对应练习：`learn/level5_ecosystem/mcp/client*.py`。

## 相关资源

* [HuggingFace MCP Course](https://huggingface.co/learn/mcp-course/unit0/introduction)
* [FastAPI-MCP](https://github.com/tadata-org/fastapi_mcp)

## 相关

- [MCP 笔记（一）：架构与通信协议](mcp-protocol.md)
- [MCP 笔记（二）：功能](mcp-features.md)
