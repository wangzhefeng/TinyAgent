# TinyAgent

TinyAgent 是一个以**「从零手写 Agent → 自研教学级框架 → 框架实战与生态」**为主线的 AI Agent 学习与实验仓库。双主线：`learn/`（L0–L6 学习路径）与 `packages/tinyagent-core`（自研框架）；载体应用 **Experiment Copilot** 面向时序预测实验仓库（默认 `~/projects/tsproj_ml`）。

协作强制规则见 [AGENTS.md](AGENTS.md)；完整文档见 [docs/README.md](docs/README.md)。

## 快速索引

| 域 | 代码 | 文档 |
|---|---|---|
| L0–L1 基础与手写 | [`learn/level0_llm_basics/`](learn/level0_llm_basics)、[`learn/level1_from_scratch/`](learn/level1_from_scratch) | [docs/10-scratch](docs/10-scratch/index.md) |
| L2 自研框架 | [`packages/tinyagent-core/`](packages/tinyagent-core)、[`learn/level2_own_framework/`](learn/level2_own_framework) | [docs/20-framework](docs/20-framework/index.md) |
| 载体应用 Copilot | [`apps/experiment_copilot/`](apps/experiment_copilot) | [docs/30-copilot](docs/30-copilot/index.md) |
| L3 LangGraph（M3） | `learn/level3_langgraph/` | [docs/40-langgraph](docs/40-langgraph/index.md) |
| L4 模式实验室（M4） | `learn/level4_patterns/` | [docs/50-patterns](docs/50-patterns/index.md) |
| L5 生态与协议 | [`learn/level5_ecosystem/`](learn/level5_ecosystem) | [docs/60-ecosystem](docs/60-ecosystem/index.md) |
| L6 评测与观测（M5） | `learn/level6_evals/`、`evals/` | [docs/70-evals](docs/70-evals/index.md) |
| 工程规范 | [`scripts/`](scripts)、[`utils/`](utils)、`tests/` | [docs/80-development](docs/80-development/index.md) |

## 快速开始

```bash
# 环境（uv，Python 3.11+）
uv sync
source .venv/bin/activate

# 配置：复制模板并填入密钥（默认智谱 OpenAI 兼容端点 + 免费档 glm-4.7-flash）
cp .env.example .env

# 文档健康检查与代码风格
python scripts/check_docs.py
uv run ruff check .
```

## 目录概览

```text
TinyAgent/
├── AGENTS.md  README.md  pyproject.toml(uv workspace)  .env.example
├── docs/               # 唯一文档中心（十域，见 docs/README.md）
├── learn/              # L0–L6 学习路径（level0_llm_basics ... level6_evals）
├── packages/tinyagent-core/  # 自研框架（导入名 tinyagent）+ examples/
├── apps/experiment_copilot/  # 载体应用（doc_qa 起步）
├── evals/  tests/      # 评测数据与测试（随里程碑建立）
├── scripts/            # check_docs.py 等
├── utils/              # 共享日志等工具
└── hello_agents/       # 框架复刻源码（M2 重构迁入 packages 后移除）
```

## 文档入口

- [学习地图与里程碑](docs/00-overview/learning-path.md)：L0–L6 各级学什么、M0–M5 执行到哪一步
- [重构方案与决策记录](docs/90-reference/refactor-plan-2026-10.md)
- [环境与模型配置](docs/00-overview/environment.md)
- [术语约定](docs/00-overview/terminology.md) ｜ [编码风格](docs/80-development/coding-style.md)
