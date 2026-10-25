> 所属：[TinyAgent Docs](../README.md) › [生态与协议](index.md)

# MCP 笔记（二）：功能

> 迁入自 `src/mcp_dev/README.md`（2026-10 拆分为三页）。

MCP 服务器通过通信协议向客户端提供的功能分为四个主要类别。通过提供具有清晰控制边界的不同类型功能，
MCP 在保持适当的安全和控制机制的同时，实现 AI 模型与外部系统之间的强大交互。

## Tools（工具）

模型可通过 MCP 调用的可执行函数或操作。

* **Control**：模型控制——LLM 根据用户请求和上下文决定何时调用。
* **Safety**：可能执行有副作用的操作，通常需要明确用户批准。
* **Use Cases**：发送消息、创建工单、查询 API、执行计算。

```python
def get_weather(location: str) -> dict:
    """Get the current weather for a specified location."""
    return {"temperature": 72, "conditions": "Sunny", "humidity": 45}
```

## Resources（资源）

对数据源的只读访问，允许模型检索上下文而无需执行复杂逻辑。

* **Control**：应用程序控制——宿主应用决定何时访问。
* **Nature**：为数据检索设计、计算量小，类似 REST 的 GET 端点。
* **Safety**：只读，安全风险低。
* **Use Cases**：访问文件内容、检索数据库记录、读取配置。

## Prompt（提示）

预定义的模板或工作流程，指导用户、模型和服务器功能之间的交互。

* **Control**：用户控制——通常在宿主 UI 中作为选项呈现，用户在模型开始处理前选择。
* **Purpose**：构建交互结构，优化工具与资源的利用。
* **Use Cases**：常见工作流程、专门任务模板、引导式交互。

## Sampling（采样）

允许服务器请求客户端（宿主应用）执行 LLM 交互。

* **Control**：服务器发起，但需客户端/宿主协助。
* **Safety**：与工具类似，通常需要用户批准。
* **Use Cases**：复杂多步任务、自主代理工作流。

采样流程：服务器发 `sampling/createMessage` 请求 → 客户端审核（可修改）→ 客户端从 LLM 采样 →
客户端审核完成内容 → 客户端将结果返回服务器。

## 功能协同工作

1. 用户选择一个提示来启动专门的流程；
2. 提示可能包含来自资源的上下文；
3. 处理过程中，模型可能调用工具执行特定操作；
4. 对复杂操作，服务器可能使用采样请求额外的 LLM 处理。

## 发现过程（Discovery）

客户端连接服务器后，可通过列表方法动态查询能力，无需硬编码：

* `tools/list`：发现可用工具
* `resources/list`：发现可用资源
* `prompts/list`：发现可用提示

## 相关

- [MCP 笔记（一）：架构与通信协议](mcp-protocol.md)
- [MCP 笔记（三）：SDK 与客户端](mcp-clients.md)
