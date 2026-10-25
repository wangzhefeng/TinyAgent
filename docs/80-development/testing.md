> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 测试

## 现状

`tests/unit/` 已建立（2026-10-25，随 M2，后随 v0.3/v0.3.1 扩到 33 个用例）：全 mock、无 API
key 可跑，覆盖 codec 解析（含 M1 冒号 bug 回归）、`@tool` Schema 生成与注册分发、`agent_loop`
工具往返 / max_steps / 错误回填自纠、session 与 tracer 往返、handoff/Swarm、开箱组件与记忆。
CI（`.github/workflows/ci.yml`）跑 ruff + check_docs + pytest 三门禁。

## 规划

| 层 | 范围 | 要求 |
|---|---|---|
| `tests/unit/` | `src/tinyagent` 框架：loop、codec、tool 注册、session、tracer、handoff、记忆 | mock LLM，无 API key 可跑，覆盖核心路径 |
| `tests/smoke/` | `learn/` 各入口：import 与 `--help` 冒烟 | 不真实调用 LLM |
| `evals/` | 应用级评测（Copilot 各版本） | 见 [70-evals](../70-evals/index.md) |

- 运行：`uv run pytest`（已含 pytest-xdist）。`pyproject.toml` 的 `[tool.pytest.ini_options]`
  声明 `pythonpath = ["."]`，使 `tests/unit/*` 中 `from tests.conftest import ...` 绝对导入
  在 console script（`uv run pytest`）下同样可用。
- 单测命名 `test_<module>.py`；夹具放 `tests/conftest.py`。
- 框架公共 API 的行为变更必须先改/补单测。
