# tinyagent

**A teaching-grade, extensible agent framework** — 一个 ~50 行的循环内核、六个可插拔协议、双工具调用编解码，以及面向真实工程的能力面（handoff/Swarm、MCP 工具源、长期记忆）。

> 本仓库同时是 AI Agent 学习实验室（`learn/` L0–L6、`apps/` 应用、`evals/` 评测），见下方 [Lab 章节](#lab-学习与应用层)。

## 安装

```bash
# 库本体（Python ≥ 3.11）
pip install tinyagent-core          # 或: uv add tinyagent-core
pip install "tinyagent-core[mcp]"   # 需要 MCP 工具源时
```

本地开发（本仓库）：

```bash
uv sync --all-extras        # 库 + dev + mcp
uv sync --all-groups        # 另含 learn/apps 所需的 course/lab 依赖
```

## 30 秒上手

```python
from tinyagent import TinyAgent, tool

@tool
def calculator(expression: str) -> str:
    """Arithmetic calculator supporting + - * / // % ** and parentheses."""
    ...

agent = TinyAgent(tools=[calculator])   # 模型配置读 .env（LLM_*，OpenAI 兼容端点）
print(agent.run("Compute (123 + 456) * 2").text)
```

可运行示例见 [`examples/`](examples/)（最小冒烟 / 编排组件 / 长期记忆 / MCP 挂载）。

## 能力面

| 能力 | 入口 | 说明 |
|---|---|---|
| 六协议内核 | `tinyagent.core.loop.agent_loop` | ChatModel / Tool / SessionStore / Tracer / Guardrail / Memory 全部可注入替换（[ADR-0001](docs/20-framework/adr/0001-agent-loop-and-protocols.md)） |
| 双 codec | `ReactTextCodec` / `NativeCodec` | ReAct 文本协议与原生 function calling 同内核切换 |
| 多智能体 | `Swarm` / `make_transfer_tools` | 移交即工具，max_handoffs 防乒乓（ADR-0004） |
| MCP 工具源 | `tinyagent.ext.mcp.MCPToolSource` | stdio 挂载任意 MCP server（ADR-0005） |
| 会话与观测 | `FileSessionStore` / `JsonlTracer` | 可恢复会话 + JSONL 事件流（ADR-0003） |
| 开箱组件 | `ReflectionAgent` / `PlanAndSolveAgent` | 生成-反思-优化 / 规划-执行（ADR-0007） |
| 长期记忆 | `ListMemory` / `FileLongTermMemory` | embedding 余弦检索，离线自动退化关键词 |

稳定导入面：`tinyagent.api`（`from tinyagent import ...`）；`0.x` 阶段 semver 起步。

## Lab（学习与应用层）

仓库下半部分是完整的 Agent 学习路径与应用实验（不打包进 wheel）：

| 层 | 代码 | 文档 |
|---|---|---|
| L0–L1 基础与手写 | [`learn/level0_llm_basics/`](learn/level0_llm_basics)、[`learn/level1_from_scratch/`](learn/level1_from_scratch) | [docs/10-scratch](docs/10-scratch/index.md) |
| L2 框架对照 | [`learn/level2_own_framework/`](learn/level2_own_framework) | [docs/20-framework](docs/20-framework/index.md) |
| L3 LangGraph 课程 | [`learn/level3_langgraph/`](learn/level3_langgraph) | [docs/40-langgraph](docs/40-langgraph/index.md) |
| L4 模式实验室 | [`learn/level4_patterns/`](learn/level4_patterns) | [docs/50-patterns](docs/50-patterns/index.md) |
| L5 生态（MCP/ADK/部署） | [`learn/level5_ecosystem/`](learn/level5_ecosystem) | [docs/60-ecosystem](docs/60-ecosystem/index.md) |
| 载体应用 Copilot | [`apps/experiment_copilot/`](apps/experiment_copilot) | [docs/30-copilot](docs/30-copilot/index.md) |
| Survey Agent | [`apps/survey_agent/`](apps/survey_agent) | [docs/70-evals](docs/70-evals/index.md) |
| 评测 | [`evals/`](evals) | [docs/70-evals](docs/70-evals/index.md) |

学习地图与里程碑见 [docs/00-overview/learning-path](docs/00-overview/learning-path.md)；项目全览见[收官总结](docs/90-reference/project-summary.md)。

## 开发

```bash
uv run pytest tests -q        # 33 项（unit + 示例冒烟，无 API key）
uv run ruff check .
python scripts/check_docs.py
```

协作规则（文档系统/编码风格/安全边界）见 [AGENTS.md](AGENTS.md)；完整文档中心见 [docs/README.md](docs/README.md)。
