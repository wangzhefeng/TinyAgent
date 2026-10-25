> 所属：[TinyAgent Docs](../README.md) › [基础与手写](index.md)

# L0–L1：基础与手写

## 定位

- **L0 LLM 基础**：chat API、流式、结构化输出、prompt chaining、路由——为一切 Agent 开发打底。
- **L1 从零手写**：不借助框架实现 ReAct / Plan-Execute / Reflection 三种范式，理解 Agent 的最小内核（生成 → 解析工具调用 → 执行 → 回填 → 终止）。

## 现状（迁移期）

| 现有代码 | 说明 | 去向 |
|---|---|---|
| `src/TinyAgent/Agent/` | 手写 ReAct（InternLM2 本地推理） | `learn/level1_from_scratch/react/`，M1 API 化 |
| `src/TinyAgent/prompt_chaining.py` | LCEL 链式调用示例 | `learn/level0_llm_basics/` |
| `src/TinyAgent/{chat_model,routing}.py` | 模型调用 / 路由骨架 | `learn/level0_llm_basics/`，routing 补完 |
| `hello_agents/test/agent_mode/` | ReAct / PlanAndSolve / Reflection 练习 | `learn/level1_from_scratch/` 对应子目录 |

## 目标

1. 三范式全部支持 OpenAI 兼容 API，无需下载本地模型即可运行（本地推理作为可选）。
2. 每个范式一个独立入口脚本 + 精简 README（学习目标 / 运行方式 / 核心代码导读）。
3. 接入 Copilot C0 只读工具（`list_configs` / `read_metrics` 等），让手写 Agent 第一次操作真实实验仓库。

## 相关

- [20-framework](../20-framework/index.md)：L2 用自研框架重写本层内容
- [50-patterns](../50-patterns/index.md)：模式全景
