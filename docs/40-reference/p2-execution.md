> 所属：[TinyAgent Docs](../README.md) › [参考资料](index.md)

# P2：安全写入、shell 与恢复

状态：**已完成（2026-10-30）**。本阶段在 P1 只读版本上增加受控写入和命令执行，默认仍保持只读，不开放任意 shell。

## 1. 已交付

- `write_file`：工作区内完整写入；`edit_file`：旧文本恰好出现一次才替换，避免长文件全量重写。
- `run_shell`：仅允许检查/查看类命令前缀，逐次审批、固定工作目录、超时和输出截断。
- 执行后端：macOS Seatbelt、Linux bubblewrap（有则启用）；初始化不可用时降级本地执行并明确警告。
- 沙箱写入仅限 workspace、临时目录和 `/dev/null`；profile 使用绝对路径，越界写入由操作系统拒绝。
- `--writable` 显式开启写入/shell；`--yes` 仅作为本次调用的显式批准，非交互场景默认拒绝。
- 同一会话串行执行；Run 取消、恢复和幂等继续复用 SQLite 事件。
- `ModelReply.usage` 与 Runtime 汇总：记录 input/output/total tokens、API/工具调用数；缺失时标 estimated/unknown，不记为零。

## 2. 使用

```bash
# 在隔离 fixture 副本中显式批准写入和检查
uv run python -m tinyagent.cli \
  --workspace results/evals/p2/workspace/run-1/fixture \
  --state results/evals/p2/state.db \
  --session p2-real \
  --writable --yes \
  run "Repair the defect, edit only allowed files, and run tests"

# 查看真实 usage
uv run python -m tinyagent.cli \
  --state results/evals/p2/state.db usage <run_id>
```

`--writable` 只开放工具，不会自动批准操作；`--yes` 会批准本次调用的所有写入和 shell，只应在隔离、可审查环境中使用。沙箱不可用时，每次写入和 shell 仍需逐条确认，无人值守拒绝。

## 3. 验证结果

- 新增 9 个 P2 用例，项目总计 **56 项测试通过**。
- 覆盖精确编辑、命令白名单、沙箱越界写入、降级、审批拒绝和 token 汇总。
- 真实模型在 fixture 副本中完成两处精确编辑：
  - `src/mini_shop/order.py`：折扣由加号修为减号；
  - `docs/configuration.txt`：默认税率由 0.2 修为 0.1。
- 普通 `uv run pytest -q` 在 Seatbelt 沙箱中 **4/4 通过**；真实 usage：8,963 input、682 output、9,645 total tokens、4 次 API 调用、4 次工具调用。
- Ruff 与文档检查全部通过。

## 4. 当前边界

- shell 采用命令白名单，不支持任意命令、联网或写工作区外路径。
- 本地降级没有硬隔离；无人值守、定时预授权和渠道白名单在 P4 实现。
- USER/MEMORY、FTS5、Skills 草稿审核和压缩前记忆在 P3 实现。
- 无 JSON-RPC、分布式队列、Graph 或多 Agent 团队。

下一阶段 P3：USER/MEMORY、FTS5、压缩前记忆和 Skills 审核复用。

## 相关

- [重构总纲](refactor-plan-product.md) ｜ [P1 执行文档](p1-execution.md) ｜ [ADR-0008](../10-framework/adr/0008-runtime-json-rpc.md) ｜ [ADR-0011](../10-framework/adr/0011-approval-execution.md)
