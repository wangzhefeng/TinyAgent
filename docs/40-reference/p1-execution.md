> 所属：[TinyAgent Docs](../README.md) › [参考资料](index.md)

# P1：CLI 单会话与只读工作区

状态：**已完成（2026-10-30）**。本阶段实现个人 Agent 的首个可运行版本，不改变旧公共 API，不开放写入或 shell。

## 1. 已交付

- CLI 单会话任务、交互聊天、按 Run 恢复、事件查看和 JSONL 导出。
- 只读工作区工具：`list_dir` / `read_file` / `search_text`，统一阻止路径穿越和符号链接越界。
- SQLite 持久化：Run、不可变事件、Session leaf、审批、幂等键和 Context 派生记录。
- ContextView：工具结果头尾截断、旧结果清理、token 估算和 tool call 配对检查，原始事件不被修改。
- Runtime：原生工具调用、错误回填、协作式取消、完成/失败恢复、审批与 usage 记录。

## 2. 代码入口

| 模块 | 职责 |
|---|---|
| `src/tinyagent/agent/` | Run/Event 类型与 ContextBuilder |
| `src/tinyagent/runtime/store.py` | SQLite 状态与 JSONL 导出 |
| `src/tinyagent/runtime/runtime.py` | 执行、取消恢复和工具调用 |
| `src/tinyagent/runtime/approvals.py` | SAFE/CONFIRM 风险与 CLI 审批 |
| `src/tinyagent/tools/workspace.py` | 只读工作区工具 |
| `src/tinyagent/channels/cli.py` | CLI 参数与交互 |
| `src/tinyagent/cli.py` | `python -m tinyagent.cli` 入口 |

## 3. 使用

```bash
# 单次只读任务
uv run python -m tinyagent.cli \
  --workspace evals/personal/workspace-task/fixture \
  --state results/evals/p1/cli/state.db \
  --session demo \
  run "Find the discount defect without modifying files"

# 同一会话交互 / 恢复 / 事件 / 导出
uv run python -m tinyagent.cli --workspace . --state results/evals/p1/cli/state.db chat
uv run python -m tinyagent.cli --state results/evals/p1/cli/state.db resume <run_id>
uv run python -m tinyagent.cli --state results/evals/p1/cli/state.db events
uv run python -m tinyagent.cli --state results/evals/p1/cli/state.db export
```

模型沿用 `LLM_*` OpenAI 兼容配置。若环境使用 SOCKS 代理且缺少支持，安装项目已声明的 `uv pip install 'httpx[socks]'`。

## 4. 验证结果

- 新增 14 个离线用例；项目总计 **47 项测试通过**。
- 覆盖截断、配对、越界、工具往返、幂等、历史恢复、取消、未知工具拒绝和 CLI 导出。
- 真实模型只读任务：正确识别 `src/mini_shop/order.py` 的折扣符号错误和 `docs/configuration.txt` 的税率漂移；未修改原始 fixture。
- `uv run pytest tests -q`、`uv run ruff check .`、`uv run python scripts/check_docs.py` 全部通过。

## 5. 当前边界

- 只读工具，无文件写入、shell、Scheduler、FTS5、USER/MEMORY 或 Skills。
- ContextView 当前实现截断与旧结果清理；摘要、压缩前记忆机会和冻结记忆快照在 P3 实现。
- usage 在模型未提供 token 明细时记 unknown/estimated，不记为零。
- 单进程、单用户；无 JSON-RPC、分布式队列、Graph 或多 Agent 团队。

下一阶段 P2：安全写入、shell、沙箱与降级、Run 取消恢复和完整 usage。

## 相关

- [重构总纲](refactor-plan-product.md) ｜ [P0 准备](p0-execution.md) ｜ [ADR-0008](../10-framework/adr/0008-runtime-json-rpc.md) ｜ [ADR-0009](../10-framework/adr/0009-event-store-sqlite.md) ｜ [ADR-0010](../10-framework/adr/0010-context-view.md)
