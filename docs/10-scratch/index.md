> 所属：[TinyAgent Docs](../README.md) › [基础与手写](index.md)

# L0–L1：基础与手写

## 定位

- **L0 LLM 基础**：chat API、链式调用、路由——为一切 Agent 开发打底。
- **L1 从零手写**：不借助框架实现 ReAct / Plan-Execute / Reflection 三种范式，理解 Agent 的最小内核（生成 → 解析工具调用 → 执行 → 回填 → 终止）。

## 现状（M1 已完成 API 化，2026-10-25）

统一从仓库根目录以 `python -m` 运行；模型由 `.env` 的 `LLM_*` 控制（默认智谱 OpenAI 兼容端点）：

| 入口 | 说明 |
|---|---|
| `learn/level0_llm_basics/llm_client.py` | **共享 Chat 客户端**：OpenAI 兼容、429 退避重试；接口对齐本地后端 |
| `python -m learn.level0_llm_basics.routing` | 路由模式：意图分类 → 四条处理链（math/translate/code/qa） |
| `learn/level0_llm_basics/prompt_chaining.py` | LCEL 链式调用（需 `OPENAI_API_KEY`，课程遗留） |
| `python -m learn.level1_from_scratch.react.agent_run` | **手写 ReAct**：模型/工具双注入；calculator 工具无外部 key 即可演示工具循环 |
| `learn/level1_from_scratch/react/llm_local.py` | 本地推理后端（可选，需 torch/transformers + downloaded_models/），与 ChatClient 同接口 |
| `learn/level1_from_scratch/react_hello_agents/` | ReAct 复刻练习（保留对照） |
| `python -m learn.level1_from_scratch.plan_execute.PlanAndSolve` | **Plan-Execute**：planner 生成步骤列表 → executor 逐步执行 |
| `python -m learn.level1_from_scratch.reflection.Reflection` | **Reflection**：生成 → 反思 → 优化循环 + Memory 轨迹 |
| `learn/level1_from_scratch/hello_agent_5min/` | 5 分钟快速上手（smolagents 风格，保留对照） |

M1 顺带修复：`agent_run.py` 的 `history=_` 误用、executor 步骤计数 bug、Serper key 模块级硬依赖改懒加载。

## 相关

- [30-copilot](../30-copilot/index.md)：C0 只读工具直接挂载本层 ReAct Agent
- [20-framework](../20-framework/index.md)：L2 用自研框架重写本层内容
