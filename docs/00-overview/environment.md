> 所属：[TinyAgent Docs](../README.md) › [概览](index.md)

# 环境搭建

## 基础环境

- Python ≥ 3.11；开发解释器以 `.python-version` 的 3.12 为准。
- 使用 [uv](https://docs.astral.sh/uv/) 管理依赖；根 `pyproject.toml` 同时定义库与个人 Agent 应用。

```bash
uv sync --all-extras       # 库、dev、mcp、socks
uv sync --group dev        # 测试与 lint
```

## 模型配置

根目录 `.env` 使用标准 `KEY=VALUE`，模板见 `.env.example`，禁止提交密钥。默认模型层使用 OpenAI 兼容端点：

| 变量 | 用途 |
|---|---|
| `LLM_PROVIDER` / `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL_ID` / `LLM_TIMEOUT` | 主模型配置，默认智谱兼容端点 |
| `DEEPSEEK_BASE_URL` / `DEEPSEEK_API_KEY` / `DEEPSEEK_MODEL_ID` | 备用 provider，按需启用 |
| `OPENAI_API_KEY` | 其他 OpenAI 兼容场景，按需启用 |

`OpenAIChatModel` 内置超时和重试。模型、提示词、fixture 和 harness 版本写入真实评测记录；usage 缺失记 unknown，不记为零。

## 工作区与状态

- 默认只读；只有显式 `--writable` 才允许写入和 shell。
- 每个应用使用独立 workspace、state 和权限配置，不默认读取真实项目。
- SQLite、USER/MEMORY、Skills、审批与投递文件位于程序 state 目录，不在 Agent workspace 内。
- `results/` 与 `logs/` 保存运行产物，不入库。

## 文档与评测检查

```bash
uv run pytest tests -q
uv run ruff check .
uv run python scripts/check_docs.py
uv run python -m evals.run_eval
```

## 相关

- [architecture](architecture.md)
- [testing](../30-development/testing.md)
- [outputs](../30-development/outputs.md)
