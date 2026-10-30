> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 测试

## 现状

`tests/unit/` 当前共 38 个用例：全 mock、无 API key 可跑，覆盖工具注册、ContextView、
SQLite/恢复、精确编辑、沙箱、学习循环，以及定时任务、隔离会话、预授权和心跳投递。
CI（`.github/workflows/ci.yml`）跑 ruff + check_docs + pytest 三门禁。

## 分层

| 层 | 范围 | 要求 |
|---|---|---|
| `tests/unit/` | `src/tinyagent` 的 Agent 循环、工具、存储、审批、记忆与调度 | mock LLM，无 API key 可跑，覆盖核心路径 |
| `evals/` | 个人任务、学习循环与例行自动化的应用级评测 | 见 [20-evals](../20-evals/index.md) |

- 运行：`uv run pytest`（已含 pytest-xdist）。`pyproject.toml` 的 `[tool.pytest.ini_options]`
  声明 `pythonpath = ["."]`，使 `tests/unit/*` 中 `from tests.conftest import ...` 绝对导入
  在 console script（`uv run pytest`）下同样可用。
- 单测命名 `test_<module>.py`；夹具放 `tests/conftest.py`。
- 框架公共 API 的行为变更必须先改/补单测。
