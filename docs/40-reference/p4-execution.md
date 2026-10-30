> 所属：[TinyAgent Docs](../README.md) › [参考资料](index.md)

# P4：Scheduler 与例行自动化

状态：**已完成（2026-10-30）**。本阶段实现持久化定时任务、隔离无人值守执行、有限预授权和本地投递，支持普通任务与心跳。

## 1. 已交付

- 任务规则：`every 30m` / `every 2h` / `daily 09:00`，最小间隔 5 分钟，最多 20 个活动任务。
- SQLite `scheduled_tasks`：到期、状态、预授权、下次执行、Run 关联、错误和投递记录。
- 先写下次时间再执行；停机错过不连续补跑，幂等键和 `delivered_run_id` 防止重复执行/投递。
- 每个 scheduled Run 使用全新隔离会话，不继承互动会话权限或记忆快照。
- 无人值守仅放行只读工具和创建时明确预授权的 `write_file`；shell 不可预授权。
- 定时任务不能创建任务、自动写记忆或修改 Skills；未授权操作默认拒绝。
- 心跳严格识别 `HEARTBEAT_OK`：无事不投递，其他输出按有事处理，usage 始终记录。
- 本地 JSONL outbox 投递，支持任务添加、列出、取消和立即执行。

## 2. 使用

```bash
# 添加立即到期的心跳任务
uv run python -m tinyagent.cli \
  --workspace evals/personal/routine-monitor \
  --state results/evals/p4/state.db \
  schedule add "every 5m" \
  "Read snapshots/base.txt and snapshots/meaningful.txt and report substantive changes." \
  --kind heartbeat --immediate

# 查看任务、执行到期任务、查看 outbox 与 usage
uv run python -m tinyagent.cli --state results/evals/p4/state.db schedule list
uv run python -m tinyagent.cli --state results/evals/p4/state.db schedule run
uv run python -m tinyagent.cli --state results/evals/p4/state.db usage <run_id>
uv run python -m tinyagent.cli --state results/evals/p4/state.db schedule cancel <task_id>
```

普通任务返回 `task`，心跳返回 `heartbeat`。预授权通过 `--allow write_file` 指定，shell 和其他高风险工具不能预授权。

## 3. 验证结果

- 新增 5 个调度用例，项目总计 **69 项测试通过**。
- 覆盖时间规则、预授权、隔离会话、重复投递防护、心跳静默和无人值守拒绝。
- 真实心跳场景：
  - 有效更新识别出全部变化并仅投递一次；
  - 无更新返回 `HEARTBEAT_OK`，没有 outbox 记录；
  - 再次执行无到期任务、无重复投递。
- 两次真实 usage 分别为 2,131 和 1,936 total tokens，各 2 次 API 调用、2 次工具调用。
- Ruff 与文档检查全部通过。

## 4. 当前边界

- 仅本地 CLI/JSONL 投递；无 Telegram/Discord、远程审批或 JSON-RPC。
- 定时任务为单进程轮询，不支持分布式队列、精确 cron、多 worker 或 Agent 团队。
- 预授权只允许明确白名单工具，不代表 shell 或本地降级具有硬隔离。
- P5 进行总验收、旧资产清理和是否替换主力工具的评审。

## 相关

- [重构总纲](refactor-plan-product.md) ｜ [P3 执行文档](p3-execution.md) ｜ [ADR-0008](../10-framework/adr/0008-runtime-json-rpc.md) ｜ [ADR-0011](../10-framework/adr/0011-approval-execution.md)
