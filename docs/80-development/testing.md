> 所属：[TinyAgent Docs](../README.md) › [工程规范](index.md)

# 测试

## 现状

测试体系尚未建立；当前质量门禁为 `python scripts/check_docs.py` 与 `uv run ruff check .`。

## 规划（随 M2 建立）

| 层 | 范围 | 要求 |
|---|---|---|
| `tests/unit/` | `packages/tinyagent` 框架：loop、codec、tool 注册、session、tracer | mock LLM，无 API key 可跑，覆盖核心路径 |
| `tests/smoke/` | `learn/` 各入口：import 与 `--help` 冒烟 | 不真实调用 LLM |
| `evals/` | 应用级评测（Copilot 各版本） | 见 [70-evals](../70-evals/index.md) |

- 运行：`uv run pytest`（已含 pytest-xdist）。
- 单测命名 `test_<module>.py`；夹具放 `tests/conftest.py`。
- 框架公共 API 的行为变更必须先改/补单测。
