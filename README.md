# tinyagent

**A self-hosted personal agent** — Python 自托管、单用户、可持续进化的个人 Agent：安全操作工作区、记住偏好、检索经验、沉淀 Skills，并定时主动完成任务。

## 安装

```bash
# Python ≥ 3.11
pip install tinyagent
pip install "tinyagent[mcp]"   # 可选 MCP 工具源
pip install "tinyagent[socks]" # 可选 SOCKS 代理支持
```

本地开发：

```bash
uv sync --all-extras
uv sync --group dev
```

模型使用 `.env` 中的 `LLM_*` OpenAI 兼容配置。

## CLI 快速开始

```bash
# 默认只读：调查工作区，不允许修改
uv run python -m tinyagent.cli \
  --workspace <工作区> --state <SQLite 状态文件> run "你的任务"

# 在隔离工作区显式启用写入和受限 shell
uv run python -m tinyagent.cli \
  --workspace <隔离工作区> --state <SQLite 状态文件> \
  --writable run "修改允许文件并运行检查"
```

- 单会话聊天、Run 取消/恢复、事件查看和 JSONL 导出。
- 写入和 shell 逐条审批，非交互环境默认拒绝；`--yes` 仅用于可审查的隔离环境。
- macOS Seatbelt / Linux bubblewrap 沙箱优先，不可用时逐条确认后本地执行。

## 能力

| 能力 | 入口 | 说明 |
|---|---|---|
| 工作区工具 | `list_dir` / `read_file` / `search_text` / `fetch_url` / `edit_file` / `run_shell` | 路径边界、精确编辑、命令白名单、页面抓取、审批与沙箱 |
| 计划模式 | `/plan` · `update_plan` / `submit_plan` | 代码强制只读调查，完整计划经审批后执行，旧计划自动折叠 |
| 持久化 | SQLite | Run、不可变事件、审批、幂等、定时任务和 usage |
| 上下文 | `ContextBuilder` | 工具结果截断、旧结果清理、摘要与 tool call 配对 |
| 长期记忆 | `USER.md` / `MEMORY.md` | 容量限制、自动写入审计、会话开始冻结快照 |
| 历史检索 | FTS5 | 同一会话多词命中，返回 event 定位与短片段 |
| Skills | `skills/` + `skill-drafts/` | 未审核不可执行，人工审核后按需加载 |
| 例行自动化 | `schedule add/list/run/cancel` | 隔离会话、有限预授权、错过不补跑、心跳投递 |

## 定时任务

```bash
uv run python -m tinyagent.cli \
  --workspace evals/personal/routine-monitor \
  --state results/evals/p4/state.db \
  schedule add "every 5m" "检查信息源并汇报更新" \
  --kind heartbeat --immediate

uv run python -m tinyagent.cli \
  --state results/evals/p4/state.db schedule run
```

定时任务使用全新隔离会话，不能创建新任务、自动写记忆或修改 Skills；shell 不允许预授权。

## 项目结构

```text
src/tinyagent/
├── api.py       # v1.0 稳定公共 API
├── agent/       # Run/Event 与 ContextView
├── core/        # 模型、消息与工具基础协议
├── runtime/     # SQLite、执行、恢复、审批、Scheduler
├── tools/       # 工作区、学习和调度工具
├── execution/   # 本地与沙箱执行后端
├── memory/      # USER/MEMORY 与冻结快照
├── skills/      # Skills 草稿与人工审核
├── channels/    # CLI
├── ext/         # 可选 MCP 工具源
└── cli.py       # 应用入口
evals/           # personal 任务契约与 fixtures
tests/           # 单元测试
docs/            # 文档中心
```

## 开发

```bash
uv run pytest tests -q        # 38 项测试
uv run ruff check .
uv run python scripts/check_docs.py
uv run python -m evals.run_eval  # 校验个人任务与 fixtures
```

协作规则见 [AGENTS.md](AGENTS.md)，文档入口见 [docs/README.md](docs/README.md)，使用说明见 [使用指南](docs/usage/guide.md)。Agent 开发学习教程见 [Nami Agent 第 11 课](docs/development/tutorials/README.md)。
