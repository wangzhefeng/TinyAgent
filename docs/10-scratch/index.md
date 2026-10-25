> 所属：[TinyAgent Docs](../README.md) › [基础与手写](index.md)

# L0–L1：基础与手写

## 定位

- **L0 LLM 基础**：chat API、流式、结构化输出、prompt chaining、路由——为一切 Agent 开发打底。
- **L1 从零手写**：不借助框架实现 ReAct / Plan-Execute / Reflection 三种范式，理解 Agent 的最小内核（生成 → 解析工具调用 → 执行 → 回填 → 终止）。

## 现状（M0 已迁入，M1 API 化改造）

| 代码 | 说明 |
|---|---|
| `learn/level0_llm_basics/prompt_chaining.py` | LCEL 链式调用（提取规格 → 转 JSON） |
| `learn/level0_llm_basics/chat_model.py` | 模型调用基础 |
| `learn/level0_llm_basics/routing.py` | 路由骨架（DeepSeek），待补完 |
| `learn/level1_from_scratch/react/` | 手写 ReAct：`Agent.py`（system prompt + Action/Observation 解析 + 两次调用）、`LLM.py`（InternLM2 本地推理）、`tool.py`（Serper 搜索）、`agent_run.py` |
| `learn/level1_from_scratch/react_hello_agents/` | ReAct 复刻练习 |
| `learn/level1_from_scratch/plan_execute/` | Plan-Execute：`PlanAndSolve.py` + `planner.py` + `executor.py` |
| `learn/level1_from_scratch/reflection/` | Reflection：`Reflection.py` + `memory.py` |
| `learn/level1_from_scratch/hello_agent_5min/` | 5 分钟快速上手（smolagents 风格） |

## M1 改造目标

1. 三范式全部改用 OpenAI 兼容 API（默认智谱 `glm-4.7-flash` 免费档），本地 transformers 推理降为可选；修 `agent_run.py` 的 `history=_` 误用。
2. 每个范式一个独立入口 + 精简说明（学习目标 / 运行方式 / 核心代码导读）。
3. 接入 Copilot C0 只读工具（`list_configs` / `read_metrics` 等），让手写 Agent 第一次操作真实实验仓库。

## 相关

- [20-framework](../20-framework/index.md)：L2 用自研框架重写本层内容
- [50-patterns](../50-patterns/index.md)：模式全景
