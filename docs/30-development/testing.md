> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 测试

## 现状

`tests/unit/` 已建立（2026-10-25，随 M2；个人 Agent P4 后共 69 个用例）：全 mock、无 API
key 可跑，覆盖 codec、工具循环、session/tracer、handoff/Swarm、记忆、ContextView/SQLite/恢复、
精确编辑、沙箱、P3 学习循环，以及 P4 定时任务、隔离会话、预授权和心跳投递。
CI（`.github/workflows/ci.yml`）跑 ruff + check_docs + pytest 三门禁。

## 规划

| 层 | 范围 | 要求 |
|---|---|---|
| `tests/unit/` | `src/tinyagent` 框架：loop、codec、tool 注册、session、tracer、handoff、记忆 | mock LLM，无 API key 可跑，覆盖核心路径 |
| `tests/smoke/` | `examples/` 各入口：import 与 `--help` 冒烟 | 不真实调用 LLM |
| `evals/` | 应用级评测（Copilot 各版本） | 见 [20-evals](../20-evals/index.md) |

- 运行：`uv run pytest`（已含 pytest-xdist）。`pyproject.toml` 的 `[tool.pytest.ini_options]`
  声明 `pythonpath = ["."]`，使 `tests/unit/*` 中 `from tests.conftest import ...` 绝对导入
  在 console script（`uv run pytest`）下同样可用。
- 单测命名 `test_<module>.py`；夹具放 `tests/conftest.py`。
- 框架公共 API 的行为变更必须先改/补单测。
