> 所属：[TinyAgent Docs](../README.md) › [生态与协议](index.md)

# MCP 笔记（一）：架构与通信协议

> 迁入自 `src/mcp_dev/README.md`（2026-10 拆分为三页）。

## 架构组件

* **Host**：宿主应用（AI 助手、IDE 等）
* **Client**：宿主内负责 MCP 通信的专用模块
* **Server**：提供外部功能的服务进程
* **tools**：可被调用的能力单元

## 通信协议：JSON-RPC 2.0

MCP 使用 JSON-RPC 2.0 作为客户端和服务器之间所有通信的消息格式：人类可读易调试、语言无关、规范明确。

三种消息类型：

1. **Requests**（客户端 → 服务器，启动操作）：含唯一标识 `id`、方法名（如 `tools/call`）、参数。

    ```json
    {
      "jsonrpc": "2.0", "id": 1, "method": "tools/call",
      "params": {"name": "weather", "arguments": {"location": "San Francisco"}}
    }
    ```

2. **Responses**（服务器 → 客户端）：与请求相同的 `id`，成功返回 `result`，失败返回 `error`（含 code 与 message）。
3. **Notifications**（单向，无需响应）：通常由服务器发送，提供事件通知或进度更新，如 `progress`。

## 传输机制

JSON-RPC 定义消息格式，MCP 另外指定传输方式，支持两种主要机制：

* **stdio**（标准输入输出）：本地通信。主应用将服务器作为子进程启动，写 `stdin`、读 `stdout`。
  优点是简单、无需网络配置、由操作系统安全沙盒化。适合文件系统访问、运行本地脚本等。
* **HTTP+SSE / Streamable HTTP**：远程通信。通过 HTTP 通信，服务器用 SSE 经持久连接推送更新；
  新版"流式 HTTP"允许按需动态升级到 SSE，兼容无服务器环境。

## 交互生命周期

1. **初始化 Initialization**：客户端连接服务器，交换协议版本与能力；客户端发 `initialize` → 服务器回
   `response`（版本+能力）→ 客户端发 `initialized` 通知确认。
2. **发现 Discovery**：客户端请求可用功能信息（`tools/list`、`resources/list`、`prompts/list`），
   服务器响应可用列表；可按类型分别重复请求。
3. **执行 Execution**：客户端按宿主需求调用功能：`tools/call` →（可选）服务器 `notification`
   进度通知 → 服务器 `response` 返回结果。
4. **终止 Termination**：不再需要时优雅关闭：客户端 `shutdown` → 服务器 `response` 确认 → 客户端 `exit`。

## 相关

- [MCP 笔记（二）：功能](mcp-features.md)
- [MCP 笔记（三）：SDK 与客户端](mcp-clients.md)
- 实现代码：`learn/level5_ecosystem/mcp/`
