<details><summary>目录</summary><p>

- [MCP](#mcp)
    - [MCP 简介](#mcp-简介)
    - [MCP 关键概念](#mcp-关键概念)
    - [MCP 架构组件](#mcp-架构组件)
    - [MCP 通信协议](#mcp-通信协议)
        - [JSON-RPC](#json-rpc)
        - [传输机制](#传输机制)
        - [交互生命周期](#交互生命周期)
    - [MCP 功能](#mcp-功能)
        - [Tools](#tools)
        - [Resources](#resources)
        - [Prompt](#prompt)
        - [Sampling](#sampling)
        - [MCP 功能协同工作](#mcp-功能协同工作)
        - [MCP 发现过程](#mcp-发现过程)
    - [MCP SDK](#mcp-sdk)
        - [SDK 概览](#sdk-概览)
        - [MCP SDKs](#mcp-sdks)
        - [MCP SDK 示例](#mcp-sdk-示例)
    - [MCP 客户端](#mcp-客户端)
        - [用户界面客户端](#用户界面客户端)
        - [配置 MCP 客户端](#配置-mcp-客户端)
            - [MCP 配置文件](#mcp-配置文件)
            - [MCP 配置示例](#mcp-配置示例)
        - [代码客户端](#代码客户端)
    - [Gradio MCP 集成](#gradio-mcp-集成)
- [相关资源](#相关资源)
</p></details><p></p>

# MCP

## MCP 简介


## MCP 关键概念


## MCP 架构组件

* Host
* Client
* Server
* tools

## MCP 通信协议

> MCP 通信协议的结构和传输机制

### JSON-RPC

MCP 使用 JSON-RPC 2.0 作为客户端和服务器之间所有通信的消息格式。JSON-RPC 是一种轻量级的远程过程调用协议，以 JSON 编码。

* 人类可读且易于调试
* 语言无关，支持在任何编程环境中实现
* 已确立，具有明确的规范和广泛的应用

MCP 协议定义了三种类型的消息：

1. Requests: 从客户端发送到服务器以启动操作，请求消息包括：
    - 唯一标识符：`id`
    - 调用方法名称：`tools/call`
    - 方法参数

    ```json
    {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "weather",
        "arguments": {
        "location": "San Francisco"
        }
    }
    }
    ```

2. Responses: 从服务器发送到客户端以回复请求，响应消息包括：
    - 与相应请求相同的 `id`
    - 成功：`result` / 失败：`error`   

    `result` 示例：

    ```json
    {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "temperature": 62,
        "conditions": "Partly cloudy"
    }
    }
    ```

    `error` 示例：

    ```json
    {
    "jsonrpc": "2.0",
    "id": 1,
    "error": {
        "code": -32602,
        "message": "Invalid location parameter"
    }
    }
    ```

3. Notificaions: 无需响应的单向消息。通常由服务器发送给客户端，以提供有关事件的通知或更新。

    ```python
    {
    "jsonrpc": "2.0",
    "method": "progress",
    "params": {
        "message": "Processing data...",
        "percent": 50
    }
    }
    ```

### 传输机制

JSON-RPC 定义了消息格式，但 MCP 还指定了客户端和服务器之间如何传输这些消息。支持两种主要的传输机制：

* `stdio`：(Standard Input/Output)
    - `stdio` 传输用于本地通信，其中客户端和服务器在同一台机器上运行：主应用程序将服务器作为子进程启动，
      并通过向其标准输入（`stdin`）写入以及从其标准输出（`stdout`）读取来与其通信。
    - 该传输的用例包括本地工具，如文件系统访问或运行本地脚本。
    - 该传输的主要优点是简单，无需网络配置，并由操作系统安全地沙盒化。
* `HTTP+SSE`: (Server-Sent Events)/Streamable HTTP
    - `HTTP+SSE` 传输用于远程通信，客户端和服务器可能位于不同的机器上：通过 HTTP 进行通信，
      服务器使用 `SSE` 通过持久连接向客户端推送更新。
    - 此传输的主要优势在于它可以在网络中工作，支持与 Web 服务的集成，并且与无服务器环境兼容。
    - MCP 标准的最新更新引入或改进了“流式 HTTP”，它通过允许服务器在需要时动态升级到 SSE 进行流式传输，
      从而提供了更大的灵活性，同时保持了与无服务器环境的兼容性。


### 交互生命周期

MCP 协议定义了客户端和服务器之间结构化的交互生命周期。

1. 初始化(Initialization)
    - 客户端连接到服务器，并交换协议版本和能力，服务器响应其支持的协议版本和能力。
    - 客户端通过通知消息确认初始化完成。

    <table style="width: 100%;">
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">→<br>initialize</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">←<br>response</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">→<br>initialized</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    </table>

2. 发现(Discovery)
    - 客户请求有关可用功能的信息，服务器响应可用工具列表。
    - 此过程可以针对每个工具、资源或提示类型重复进行。

    <table style="width: 100%;">
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">→<br>tools/list</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">←<br>response</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    </table>

3. 执行(Execution)
    - 客户端根据主机需求调用功能。

    <table style="width: 100%;">
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">→<br>tools/call</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">←<br>notification (optional progress)</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">←<br>response</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    </table>

4. 终止(Termination)
    - 当不再需要时，连接会优雅地关闭，并且服务器会确认关闭请求。
    - 客户端发送最终的退出消息以完成终止。

    <table style="width: 100%;">
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">→<br>shutdown</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">←<br>response</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    <tr>
        <td style="background-color: lightgreen; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">💻</td>
        <td style="text-align: center;">→<br>exit</td>
        <td style="background-color: lightblue; text-align: center; padding: 10px; border: 1px solid #ccc; border-radius: 4px;">🌐</td>
    </tr>
    </table>

## MCP 功能

MCP 服务器通过通信协议向客户端提供各种功能。这些功能分为四个主要类别，每个类别都有其独特的特征和使用场景。

> 结论：通过提供具有清晰控制边界的不同类型功能，MCP 能够在保持适当的安全和控制机制的同时，
> 实现 AI 模型与外部系统之间的强大交互。

### Tools

> 工具

工具是 AI 模型可以通过 MCP 协议调用的可执行函数或操作。

* Control
    - 工具通常是模型控制的，这意味着 AI 模型（LLM）根据用户的请求和上下文决定何时调用它们。
* Safety
    - 由于它们能够执行具有副作用的操作，因此工具执行可能很危险。因此，它们通常需要明确用户批准。
* Use Cases
    -  发送消息
    -  创建工单
    -  查询 API
    -  执行计算

示例：

```python
def get_weather(location: str) -> dict:
    """Get the current weather for a specified location."""
    # Connect to weather API and fetch data
    return {
        "temperature": 72,
        "conditions": "Sunny",
        "humidity": 45
    }
```


### Resources

> 资源

资源提供只读访问数据源，允许 AI 模型在不执行复杂逻辑的情况下检索上下文。

* Control
    - 资源由应用程序控制，这意味着主机应用程序通常决定何时访问它们。
* Nature
    - 它们是为数据检索而设计的，计算量最小，类似于 REST API 中的 GET 端点。
* Safety
    - 由于它们是只读的，因此它们通常比工具具有较低的安全风险。
* Use Cases
    - 访问文件内容、检索数据库记录、读取配置信息。

示例：

```python
def read_file(file_path: str) -> str:
    """Read the contents of a file at the specified path."""
    with open(file_path, 'r') as f:
        return f.read()
```

### Prompt

> 提示

提示是预定义的模板或工作流程，指导用户、AI 模型和服务器功能之间的交互。

* Control
    - 提示由用户控制，通常在主机应用程序的 UI 中作为选项呈现。
* Purpose
    - 它们构建交互结构，以优化可用工具和资源的利用。
* Selection
    - 用户通常在 AI 模型开始处理之前选择一个提示，为交互设置上下文。
* Use Cases
    - 常见的工作流程、专门的任务模板、引导式交互。

示例：

```python
def code_review(code: str, language: str) -> list:
    """Generate a code review for the provided code snippet."""
    return [
        {
            "role": "system",
            "content": f"You are a code reviewer examining {language} code. Provide a detailed review highlighting best practices, potential issues, and suggestions for improvement."
        },
        {
            "role": "user",
            "content": f"Please review this {language} code:\n\n```{language}\n{code}\n```"
        }
    ]
```

### Sampling

> 采样

采样允许服务器请求客户端（特别是主机应用程序）执行 LLM 交互。

* Control
    - 采样是服务器发起的，但需要客户端/主机应用程序的协助。
* Purpose
    - 它支持服务器驱动的代理行为，并可能实现递归或多步骤交互。
* Safety
    - 与工具类似，采样操作通常需要用户批准。
* Use Cases
    - 复杂的多步骤任务、自主代理工作流、交互式流程。

示例：

```python
def request_sampling(messages, system_prompt=None, include_context="none"):
    """Request LLM sampling from the client."""
    # In a real implementation, this would send a request to the client
    return {
        "role": "assistant",
        "content": "Analysis of the provided data..."
    }
```

采样流程遵循以下步骤：

1. 服务器向客户端发送 `sampling/createMessage` 请求；
2. 客户端审核请求并可以修改它；
3. 客户端从 LLM 中采样；
4. 客户端审核完成内容；
5. 客户端将结果返回给服务器。

### MCP 功能协同工作


上述功能旨在以互补的方式协同工作：

1. 用户可能选择一个提示来启动一个专门的流程；
2. 提示可能包含来自资源的上下文；
3. 在处理过程中，AI 模型可能会调用工具来执行特定操作；
4. 对于复杂的操作，服务器可能会使用采样来请求额外的 LLM 处理。

这些原语之间的区别为 MCP 交互提供了一个清晰的结构，使 AI 模型能够在保持适当控制边界的同时访问信息、
执行操作并参与复杂的工作流程。

### MCP 发现过程

> Discovery Process

MCP 的一个关键特性是动态能力发现。当客户端连接到服务器时，它可以通过特定的列表方法查询可用的工具、
资源和提示：

* `tools/list`：发现可用工具
* `resources/list`：发现可用资源
* `prompts/list`：发现可用提示

这种动态发机制允许客户端适应每个服务器提供的特定功能，而无需硬编码服务器的功能知识。

## MCP SDK

### SDK 概览

模型上下文协议为 JavaScript、Python 和其他语言提供了官方 SDK。这使得在您的应用程序中实现 MCP 客户端和服务器变得容易。
这些 SDK 处理底层的协议细节，让您能够专注于构建应用程序的功能。

两个 SDK 提供相似的核心功能，遵循我们之前讨论的 MCP 协议规范。它们处理：

* 协议级别的通信
* 能力注册与发现
* 消息序列化/反序列化
* 连接管理
* 错误处理

### MCP SDKs

* [Python SDK: https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
* [Model Context Protocol](https://modelcontextprotocol.io/introduction)

### MCP SDK 示例


```python
# server.py

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Weather Service")


@mcp.tool()
def get_weather(location: str) -> str:
    """
    Get the current weather for a specified location.
    """
    return f"Weather in {location}: Sunny, 72°F" 


@mcp.resource("weather://{location}")
def weather_resource(location: str) -> str:
    """
    Provide weather data as a resource
    """
    return f"Weather data for {location}: Sunny, 72°F"


@mcp.prompt()
def weather_report(location: str) -> str:
    """
    Create a weather report prompt.
    """
    return f"""You are a weather reporter. Weather report for {location}?"""




# 测试代码 main 函数
def main():
    mcp.run(transport="sse", port = "3001")

if __name__ == "__main__":
    main()
```

```bash
$ mcp dev server.py
```

## MCP 客户端

MCP 客户端是至关重要的组件，它们充当 AI 应用（主机）和 MCP 服务器提供的外部功能之间的桥梁。
将主机视为您的主要应用（如 AI 助手或 IDE），而客户端则是主机中负责处理 MCP 通信的专用模块。

### 用户界面客户端

* 聊天界面客户端
    - Anthropic 的 Claude 桌面是其中一个最突出的 MCP 客户端，提供与各种 MCP 服务器的集成
* 交互式开发客户端
    - Cursor 的 MCP 客户端实现通过直接集成代码编辑功能，实现了 AI 驱动的编码辅助。
      它支持多个 MCP 服务器的连接，并在编码过程中提供实时工具调用，成为开发人员的强大工具。
    - Continue.dev 是另一个支持 MCP 并从 VS Code 连接到 MCP 服务器的交互式开发客户端的例子。

### 配置 MCP 客户端

MCP 服务器和客户端的有效部署需要适当的配置。

> MCP 规范仍在不断发展中，因此配置方法也处于不断变化中。我们将专注于当前的最佳实践。

#### MCP 配置文件

MCP 主机使用配置文件来管理服务器连接。这些文件定义了哪些服务器可用以及如何连接到它们。
配置文件非常简单、易于理解，并且在主要的 MCP 主机之间保持一致。

`mcp.json` 结构：MCP 的标准配置文件名为 `mcp.json`。以下是基本结构：

```json
{
  "servers": [
    {
      "name": "Server Name",
      "transport": {
        "type": "stdio|sse",
        // Transport-specific configuration
      }
    }
  ]
}
```

* `stdio` 传输配置：对于使用标准输入输出传输的本地服务器，配置包括启动服务器进程的命令和参数：

```json
{
  "servers": [
    {
      "name": "File Explorer",
      "transport": {
        "type": "stdio",
        "command": "python",
        "args": ["/path/to/file_explorer_server.py"]
      }
    }
  ]
}
```

* HTTP+SSE 传输配置

对于使用 HTTP+SSE 传输的远程服务器，配置包括服务器 URL：

```python
{
  "servers": [
    {
      "name": "Remote API Server",
      "transport": {
        "type": "sse",
        "url": "https://example.com/mcp-server"
      }
    }
  ]
}
```

* 配置中的环境变量

可以使用 `env` 字段将环境变量传递给服务器进程。以下是在服务器代码中如何访问它们：

在 Python 中，使用 `os` 模块来访问环境变量：

```python
# github_server.py

import os

# Access environment variables
github_token = os.environ.get("GITHUB_TOKEN")
if not github_token:
    raise ValueError("GITHUB_TOKEN environment variable is required")

# Use the token in your server code
def make_github_request():
    headers = {"Authorization": f"Bearer {github_token}"}
    # ... rest of your code
```

`mcp.json` 中的相应配置将如下所示：

```json
{
  "servers": [
    {
      "name": "GitHub API",
      "transport": {
        "type": "stdio",
        "command": "python",
        "args": ["/path/to/github_server.py"],
        "env": {
          "GITHUB_TOKEN": "your_github_token"
        }
      }
    }
  ]
}
```

#### MCP 配置示例

场景 1：本地服务器配置

* 在此场景中，我们有一个本地服务器，它是一个 Python 脚本，可能是一个文件浏览器或代码编辑器。

```json
{
  "servers": [
    {
      "name": "File Explorer",
      "transport": {
        "type": "stdio",
        "command": "python",
        "args": ["/path/to/file_explorer_server.py"]
      }
    }
  ]
}
```

场景 2：远程服务器配置

* 在此场景中，我们有一个远程服务器，它是一个天气 API。

```json
{
  "servers": [
    {
      "name": "Weather API",
      "transport": {
        "type": "sse",
        "url": "https://example.com/mcp-server"
      }
    }
  ]
}
```

### 代码客户端

> code clients

也可以在代码中使用 MCP 客户端，以便工具可用于 LLM。

* 首先，让我们从上一页探索我们的天气服务器。在 `smolagents` 中，
  我们可以使用 `ToolCollection` 类来自动发现和注册来自 MCP 服务器的工具。
  这是通过将 `StdioServerParameters` 或 `SSEServerParameters` 传递给 `ToolCollection.from_mcp` 方法来完成的。
  然后我们可以将工具打印到控制台。

```python
from smolagents import ToolCollection, CodeAgent
from mcp.client.stdio import StdioServerParameters

server_parameters = StdioServerParameters(command="uv", args=["run", "server.py"])

with ToolCollection.from_mcp(
    server_parameters, trust_remote_code=True
) as tools:
    print("\n".join(f"{t.name}: {t.description}" for t in tools))
```

也可以连接到托管在远程机器上的 MCP 服务器。在这种情况下，我们需要将 `SSEServerParameters` 传递给 `ToolCollection.from_mcp` 方法。

```python
from smolagents.mcp_client import MCPClient

with MCPClient(
    {"url": "https://abidlabs-mcp-tools.hf.space/gradio_api/mcp/sse"}
) as tools:
    # Tools from the remote server are available
    print("\n".join(f"{t.name}: {t.description}" for t in tools))
```

现在，让我们看看如何在代码代理中使用 MCP 客户端。

```python
from smolagents import ToolCollection, CodeAgent
from mcp.client.stdio import StdioServerParameters
from smolagents import CodeAgent, InferenceClientModel

model = InferenceClientModel()

server_parameters = StdioServerParameters(command="uv", args=["run", "server.py"])

with ToolCollection.from_mcp(
    server_parameters, trust_remote_code=True
) as tool_collection:
    agent = CodeAgent(tools=[*tool_collection.tools], model=model)
    agent.run("What's the weather in Tokyo?")
```

我们也可以连接到 MCP 包。这里是一个连接到 `pubmedmcp` 包的示例。

```python
from smolagents import ToolCollection, CodeAgent
from mcp import StdioServerParameters

server_parameters = StdioServerParameters(
    command="uv",
    args=["--quiet", "pubmedmcp@0.1.3"],
    env={"UV_PYTHON": "3.12", **os.environ},
)

with ToolCollection.from_mcp(server_parameters, trust_remote_code=True) as tool_collection:
    agent = CodeAgent(tools=[*tool_collection.tools], add_base_tools=True)
    agent.run("Please find a remedy for hangover.")
```

## Gradio MCP 集成




# 相关资源

* [huggingface/mcp-course](https://huggingface.co/learn/mcp-course/unit0/introduction)
* [FastAPI-MCP](https://github.com/tadata-org/fastapi_mcp)
