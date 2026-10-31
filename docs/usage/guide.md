> 所属：[TinyAgent Docs](../README.md) › 使用

# 使用指南

## 1. 安装与模型配置

要求 Python ≥ 3.11，使用 uv 安装依赖：

```bash
uv sync --all-extras
```

在仓库根目录 `.env` 配置 OpenAI 兼容模型，不要提交该文件：

```bash
LLM_BASE_URL=...
LLM_API_KEY=...
LLM_MODEL_ID=...
LLM_TIMEOUT=60
```

可选 extras：`tinyagent[mcp]` 提供 MCP 工具源，`tinyagent[socks]` 提供 SOCKS 代理支持。

## 2. 工作区与状态

- `--workspace`：Agent 可访问的目录，默认只读；根目录可放 `AGENTS.md` 项目说明，截断后常驻系统提示。
- `--state`：SQLite 状态文件；其所在目录还保存 USER/MEMORY、Skills 和 outbox。
- 状态目录应位于 workspace 外；不同任务使用独立 workspace 和 state。
- 本地体验可使用 `results/local-demo/workspace` 与 `results/local-demo/state.db`。
- state 目录旁可放 `mcp.json` 接入 MCP 工具源（需安装 `tinyagent[mcp]`）：

```json
{"servers": {"demo": {"command": "python", "args": ["server.py"], "safe_tools": ["now"]}}}
```

工具以 `mcp__服务器__工具` 名注册，进入统一审批路径；仅 `safe_tools` 点名的工具视为只读，其余逐次审批。单个服务器启动失败不影响其余服务器。

## 3. 执行任务

```bash
# 单次只读任务
uv run python -m tinyagent.cli \
  --workspace results/local-demo/workspace \
  --state results/local-demo/state.db \
  run "分析当前工作区并总结"

# 持续会话
uv run python -m tinyagent.cli \
  --workspace results/local-demo/workspace \
  --state results/local-demo/state.db \
  --session daily \
  chat
```

交互中输入 `/events` 查看事件，输入 `/exit` 退出；输入 `/plan 任务` 进入计划模式：先只读调查（有副作用的工具会被代码拒绝），Agent 调用 `submit_plan` 提交完整计划并经你批准后才开始修改。使用相同 state 可保留会话、记忆和定时任务。

## 4. 写入、shell 与网络抓取

```bash
uv run python -m tinyagent.cli \
  --workspace results/local-demo/workspace \
  --state results/local-demo/state.db \
  --writable \
  run "修改允许文件并运行检查"
```

`--writable` 只开放能力，写入和 shell 仍需逐项审批，审批提示展示真实参数（命令、写入内容预览）；拒绝时可附原因回传给模型，`write_file` 可选「本次运行一直允许」。`--yes` 会批准本次调用的全部写入和 shell，仅用于可审查的隔离环境。macOS 使用 Seatbelt、Linux 使用 bubblewrap；沙箱不可用时本地降级没有硬隔离。`fetch_url` 抓取 http/https 页面文本，同样逐次审批；不可预授权，无人值守的定时任务中默认拒绝。

## 5. 定时任务

```bash
uv run python -m tinyagent.cli \
  --workspace results/local-demo/workspace \
  --state results/local-demo/state.db \
  schedule add "every 5m" "检查信息源并汇报更新" \
  --kind heartbeat --immediate

uv run python -m tinyagent.cli \
  --state results/local-demo/state.db schedule run
```

支持 `every 30m`、`every 2h`、`daily 09:00`，最小间隔 5 分钟。定时任务使用独立会话，不自动写记忆或修改 Skills，shell 不可预授权；心跳无事不投递。

## 6. 运行记录

CLI 还提供 `resume`、`usage`、`events`、`export`，分别用于恢复 Run、查看用量、查看事件和导出 JSONL。通过对应命令的 `--help` 查看参数。

`results/` 保存运行产物、评测结果和本地状态，`logs/` 保存按需启用的日志；两者都不入库。当前没有 HTTP 服务、Web UI 或后台守护进程，直接运行 CLI 即可体验。

## 相关

- [架构概览](../architecture/overview.md) ｜ [评测规范](../evaluation/scenarios.md)
