> 所属：[TinyAgent Docs](../README.md) › [概览](index.md)

# 环境搭建

## 基础环境

- Python ≥ 3.11；[uv](https://docs.astral.sh/uv/) 管理依赖与虚拟环境。
- 开发解释器钉定：`.python-version`（3.12，与 CI 一致，2026-10-25 添加）；库本身的兼容下限仍为 `requires-python = ">=3.11"`。
- 仓库即库（2026-10-25 库化，发行名已统一为 `tinyagent`）：根 `pyproject.toml` 就是 `tinyagent` 包（src 布局）；learn/apps 依赖按组安装（`uv sync --all-groups`）。

```bash
uv sync
source .venv/bin/activate
```

## 配置（.env）

根目录 `.env` 为标准 `KEY=VALUE`（模板见根 `.env.example`，勿提交密钥）。默认 provider 为智谱 BigModel 的 **OpenAI 兼容端点**（[官方文档](https://docs.bigmodel.cn/cn/guide/develop/openai/introduction)）：

| 变量 | 用途 |
|---|---|
| `LLM_PROVIDER` / `LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL_ID` / `LLM_TIMEOUT` | 主 LLM 配置；默认 `zhipu` + `https://open.bigmodel.cn/api/paas/v4` + `glm-4.7-flash`（免费档） |
| `DEEPSEEK_BASE_URL` / `DEEPSEEK_API_KEY` / `DEEPSEEK_MODEL_ID` | 备用 provider（**按需使用，尽量不用**） |
| `ZHIPU_ANTHROPIC_BASE_URL` / `ZHIPU_CODING_PLAN_MODEL` | Coding Plan 的 Anthropic 兼容端点（仅限官方指定工具，项目脚本不直用） |
| `GOOGLE_SERPER_API_KEY` | L1 手写 ReAct 的搜索工具（按需启用） |
| `OPENAI_API_KEY` | L3 LangGraph 课程默认栈（按需启用） |
| `MODELSCOPE_API_KEY` | hello_agents 旧接口迁移期兼容（可选） |

模型阶梯与计费：

- **默认尝试免费档 `glm-4.7-flash`**（输入/输出/缓存均免费，见 [API 定价](https://docs.bigmodel.cn/cn/guide/start/pricing.md)）；**2026-10-25 实测**：该 key 调用免费档返回 429/1314「套餐已失效」，故 `.env` 当前为 `glm-5.3-flash`（¥0.8 / ¥2.8 每百万 token）。免费档恢复后改回一行即可。
- `ChatClient` 内置 429 指数退避重试；强推理任务 `glm-5.3`（¥8 / ¥28）。
- DeepSeek 为最后备用（付费，尽量不用）；M2 框架的 retry / 降级钩子会把该阶梯自动化。
- `glm-5.3-flash` 默认输出思考过程（`reasoning_content`），低延迟场景可通过 `extra_body` 的 `thinking.type`（enabled / disabled）控制。
- `TPROJ_ML_ROOT`：Copilot 默认操作仓库路径（默认 `~/projects/tsproj_ml`）。

## 运行约定

- 脚本一律从**仓库根目录**运行。
- 日志：`utils/log_util.py`，输出到 stderr 与 `logs/<LOG_NAME>/`（`LOG_NAME` 由各脚本设置）。
- 数据 / 模型 / 产物目录：`dataset/`、`downloaded_models/`、`results/`、`logs/` 均不入库，约定详见 [outputs](../80-development/outputs.md)。

## 文档检查

```bash
python scripts/check_docs.py
```

## 相关

- [coding-style](../80-development/coding-style.md)
- [testing](../80-development/testing.md)
